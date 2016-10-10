import calendar
from datetime import datetime, time, timedelta

import numpy as np
import pandas as pd
import pytz
from sqlalchemy import orm
from sqlalchemy.orm import relationship
from webapp import db
from .generation import Generation
from .turbine import Turbine
from .turbine_power_curve import TurbinePowerCurve
from .optimization_results import OptimizationResults
from .optimization_job import OptimizationJob


class Windpark(db.Model):
    __tablename__ = 'windparks'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), index=True)
    location_id = db.Column(db.Integer(), db.ForeignKey('locations.id'), index=True)
    market_id = db.Column(db.Integer(), db.ForeignKey('markets.id'))
    data_source = db.Column(db.String(255), default='turbines')
    optimization_results = db.Column(OptimizationResults())
    optimization_job = db.Column(OptimizationJob())

    location = relationship('Location', back_populates='windparks')
    market = relationship('Market', back_populates='windparks')
    generation = relationship('Generation', back_populates='windpark', order_by='Generation.time',
                              cascade='all, delete-orphan')
    turbines = relationship('WindparkTurbine', back_populates='windpark',
                            cascade='all, delete-orphan')

    def __init__(self, *args, **kwargs):
        super(Windpark, self).__init__(*args, **kwargs)
        self.power_curve = None

    @orm.reconstructor
    def init_on_load(self):
        self.power_curve = None

    @classmethod
    def from_excess_args(cls, **kwargs):
        d = {}
        for c in cls.__table__.columns:
            d[c.name] = kwargs.get(c.name)
        item = Windpark(**d)
        return item

    def to_dict(self):
        d = {}
        for c in ('id', 'name', 'data_source'):
            d[c] = getattr(self, c)
        d['location'] = None if self.location is None else self.location.to_dict()
        d['market'] = None if self.market is None else self.market.to_dict()
        turbines = []
        for rel in self.turbines:
            turbine = db.session.query(Turbine).filter_by(id=rel.turbine_id).first()
            turbines.append({'count': rel.count,
                             'relationship_id': rel.id,
                             'turbine_id': rel.turbine_id,
                             'name': turbine.name,
                             'rated_power': turbine.rated_power})
        d['turbines'] = turbines
        d[
            'optimization_job'] = OptimizationJob().to_dict() if self.optimization_job is None else self.optimization_job.to_dict()
        return d

    def update_from_dict(self, d):
        for c in self.__table__.columns:
            if c.name in d:
                setattr(self, c.name, d[c.name])

    def add_generation(self, df):
        for ts in df.index:
            gen = db.session.query(Generation).filter_by(windpark_id=self.id, time=ts).first()
            if gen is None:
                gen = Generation(windpark_id=self.id, time=ts)
                db.session.add(gen)
            for name in df.columns.values:
                setattr(gen, name, df[name][ts])
        db.session.commit()

    def get_summary(self):
        start = self.generation[0].time.replace(tzinfo=pytz.utc)
        end = self.generation[-1].time.replace(tzinfo=pytz.utc)
        result = {'start': calendar.timegm(start.timetuple()) * 1000,
                  'end': calendar.timegm(end.timetuple()) * 1000}
        values = []
        for gen in self.generation:
            values.append(getattr(gen, 'power'))
        values = np.array(values, dtype=np.float)
        values = values[np.isfinite(values)]
        value_max = np.max(values) if values.size > 0 else None
        value_min = np.min(values) if values.size > 0 else None
        value_mean = np.mean(values) if values.size > 0 else None
        value_std = np.std(values) if values.size > 0 else None
        result['max'] = value_max
        result['min'] = value_min
        result['mean'] = value_mean
        result['std'] = value_std
        return result

    def get_total_power_curve(self):
        self._calculate_total_power_curve()
        if self.power_curve is None:
            return None
        else:
            return [[x[0], x[1] / 1000.0] for x in self.power_curve.values]

    def _calculate_total_power_curve(self):
        if self.data_source != 'turbines':
            raise Exception('Power curve from this source is unreliable and not supported')
        collected_curves = None
        for turbine_rel in self.turbines:
            curve = pd.read_sql(db.session.query(TurbinePowerCurve.wind_speed, TurbinePowerCurve.power)
                                .filter_by(turbine_id=turbine_rel.turbine_id).statement,
                                db.session.bind)
            curve.loc[:, 'power'] *= turbine_rel.count
            if collected_curves is None:
                collected_curves = curve
            else:
                collected_curves['power'] += curve['power']
        self.power_curve = collected_curves

    def simulate_generation(self, date, time_span, n_scenarios, da_am_time_span, n_da_am_scenarios, adjusted=False):
        if self.location is None:
            raise Exception('Cannot simulate generation for undefined location')

        if self.power_curve is None:
            self._calculate_total_power_curve()
        # _, simulated_wind = self.location.simulate_wind_2stage(time_span, n_scenarios, da_am_time_span,
        #                                                        n_da_am_scenarios)
        forecasted_wind, simulated_wind, dates = self.location.simulate_wind_with_forecast(date, time_span, n_scenarios,
                                                                                           da_am_time_span,
                                                                                           n_da_am_scenarios)
        simulated_wind = np.array(simulated_wind) / 3.6
        simulated_power = np.interp(simulated_wind, self.power_curve['wind_speed'], self.power_curve['power']) / 1000.0

        if adjusted:
            forecasted_wind = (np.array(forecasted_wind) + self.location.forecast_error_model.coef['intercept']) / 3.6
        else:
            forecasted_wind = np.array(forecasted_wind) / 3.6
        forecasted_power = np.interp(forecasted_wind, self.power_curve['wind_speed'],
                                     self.power_curve['power']) / 1000.0

        return simulated_wind, simulated_power, forecasted_wind, forecasted_power, dates

    def simulate_market(self, date, start_hour, time_span, n_lambdaD_scenarios, n_MAvsMD_scenarios, n_sqrt_r_scenarios):
        if self.market is None:
            raise Exception('Cannot simulate market for undefined market')

        timezone_name = self.location.tz_long
        timezone = pytz.timezone(timezone_name)
        start_dt = datetime.combine(date, time(0, 0, 0, 0))
        start_dt_location_tz = timezone.localize(start_dt) + timedelta(hours=start_hour)

        start_dt_utc = start_dt_location_tz.astimezone(pytz.UTC)
        start_hour_utc = start_dt_utc.hour
        simulated_lambdaD, simulated_MAvsMD, simulated_sqrt_r = self.market.simulate_prices(start_hour_utc, time_span,
                                                                                            n_lambdaD_scenarios,
                                                                                            n_MAvsMD_scenarios,
                                                                                            n_sqrt_r_scenarios)
        return simulated_lambdaD, simulated_MAvsMD, simulated_sqrt_r
