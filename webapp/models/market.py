from collections import defaultdict
import csv
import logging
import math
import cStringIO
from datetime import datetime, timedelta

import pytz
import numpy as np
from sqlalchemy.orm import relationship






# from rpy2.robjects.packages import importr
import rpy2.robjects as ro
from rpy2.robjects import numpy2ri

# forecast = importr("forecast")
r_source = ro.r['source']
r_source('webapp/models/arima_condsim.R')

from webapp import db
from .prices import Prices
from .arima_price_model import ArimaPriceModel


class Market(db.Model):
    __tablename__ = 'markets'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), index=True)
    lambdaD_model = db.Column(ArimaPriceModel())
    MAvsMD_model = db.Column(ArimaPriceModel())
    sqrt_r_model = db.Column(ArimaPriceModel())

    prices = relationship('Prices', back_populates='market', order_by='Prices.time',
                          cascade='all, delete-orphan')
    windparks = relationship('Windpark', back_populates='market', cascade='all')

    @classmethod
    def from_excess_args(cls, **kwargs):
        d = {}
        for c in cls.__table__.columns:
            d[c.name] = kwargs.get(c.name)
        item = Market(**d)
        return item

    def to_dict(self):
        d = {}
        for c in ('id', 'name', 'user_id'):
            d[c] = getattr(self, c)
        return d

    def add_prices(self, df):
        for ts in df.index:
            prices = db.session.query(Prices).filter_by(market_id=self.id, time=ts).first()
            if prices is None:
                prices = Prices(market_id=self.id, time=ts)
                db.session.add(prices)
            for name in df.columns.values:
                setattr(prices, name, df[name][ts])
        db.session.commit()

    def get_summary(self):
        n_prices = len(self.prices)
        start = self.prices[0].time.replace(tzinfo=pytz.utc)
        end = self.prices[-1].time.replace(tzinfo=pytz.utc)
        result = {'n_prices': n_prices, 'start': start, 'end': end}
        for name in ('lambdaD', 'lambdaA', 'MAvsMD', 'lambdaPlus', 'lambdaMinus', 'r_pos', 'r_neg', 'sqrt_r'):
            values = []
            for price in self.prices:
                values.append(getattr(price, name))
            values = np.array(values, dtype=np.float)
            values = values[np.isfinite(values)]
            value_max = np.max(values) if values.size > 0 else None
            value_min = np.min(values) if values.size > 0 else None
            value_mean = np.mean(values) if values.size > 0 else None
            value_std = np.std(values) if values.size > 0 else None
            result[name] = {'max': value_max,
                            'min': value_min,
                            'mean': value_mean,
                            'std': value_std}
        for name in ('lambdaD_model', 'MAvsMD_model', 'sqrt_r_model'):
            value = getattr(self, name)
            if value is not None:
                value = value.to_dict()
            result[name] = value
        return result

    def calculate_missing_values(self):
        for price in self.prices:
            if price.lambdaD is not None and price.lambdaA is not None and price.MAvsMD is None:
                price.MAvsMD = price.lambdaA - price.lambdaD
            if price.lambdaD is not None and price.lambdaPlus is not None and price.r_pos is None:
                price.r_pos = price.lambdaPlus / price.lambdaD
            if price.lambdaD is not None and price.lambdaMinus is not None and price.r_neg is None:
                price.r_neg = price.lambdaMinus / price.lambdaD
            if price.r_pos is not None and price.r_neg is not None and price.sqrt_r is None:
                price.sqrt_r = math.sqrt(price.r_pos + price.r_neg - 1)

    def fit_price_model(self):
        lambdaD = []
        MAvsMD = []
        sqrt_r = []
        for price in self.prices:
            lambdaD.append(price.lambdaD)
            MAvsMD.append(price.MAvsMD)
            sqrt_r.append(price.sqrt_r)

        lambdaD = np.array(lambdaD, dtype=np.float)
        values = np.log(lambdaD)  # [np.isfinite(lambdaD)])
        self.lambdaD_model = ArimaPriceModel()
        self.lambdaD_model.set_parameters(p=2, d=0, q=1, P=1, D=1, Q=1, m=24)
        self.lambdaD_model.fit(values)

        MAvsMD = np.array(MAvsMD, dtype=np.float)
        # MAvsMD = MAvsMD[np.isfinite(MAvsMD)]
        self.MAvsMD_model = ArimaPriceModel()
        self.MAvsMD_model.set_parameters(p=1, d=0, q=11, P=1, D=0, Q=1, m=24)
        self.MAvsMD_model.fit(MAvsMD)

        sqrt_r = np.array(sqrt_r, dtype=np.float)
        # sqrt_r = sqrt_r[np.isfinite(sqrt_r)]
        self.sqrt_r_model = ArimaPriceModel()
        self.sqrt_r_model.set_parameters(p=2, d=0, q=1, P=1, D=0, Q=1, m=24)
        self.sqrt_r_model.fit(sqrt_r)

    def get_csv(self):
        csv_file = cStringIO.StringIO()
        fields = ['time', 'lambdaD', 'lambdaA', 'MAvsMD', 'lambdaPlus', 'lambdaMinus', 'r_pos', 'r_neg', 'sqrt_r']
        writer = csv.writer(csv_file)
        writer.writerow(fields)

        for prices in self.prices:
            writer.writerow([getattr(prices, name) for name in fields])
        return csv_file.getvalue()

    def is_recent_prices(self, date, start_hour):
        if len(self.prices) == 0:
            return False
        last_prices = self.prices[-1]
        if last_prices.MAvsMD is None or last_prices.lambdaD is None or last_prices.sqrt_r is None:
            return False
        da_start_datetime = datetime(year=date.year, month=date.month, day=date.day, hour=start_hour, tzinfo=pytz.utc)
        prev_hour = da_start_datetime - timedelta(hours=1)
        return last_prices.time >= prev_hour

    def simulate_prices(self, simulation_start_hour, time_span, n_da_price_scenarios, n_da_am_price_scenarios,
                        n_adj_price_scenarios):

        if self.lambdaD_model is None or self.MAvsMD_model is None or self.sqrt_r_model is None:
            raise Exception('Unable to simulate prices without model')

        time_after_last = None
        for price in self.prices:
            if price.time.hour == simulation_start_hour:
                time_after_last = price.time

        seeds = defaultdict(list)

        for price in self.prices:
            if price.time >= time_after_last:
                break
            seeds['lambdaD'].append(price.lambdaD)
            seeds['MAvsMD'].append(price.MAvsMD)
            seeds['sqrt.r'].append(price.sqrt_r)

        # find first range without NaNs in all prices searching from end, jumping by whole days
        while True:
            if (all([x is not None for x in seeds['lambdaD'][-100:]]) and
                    all([x is not None for x in seeds['MAvsMD'][-100:]]) and
                    all([x is not None for x in seeds['sqrt.r'][-100:]])):
                break
            seeds['lambdaD'] = seeds['lambdaD'][:-24]
            seeds['MAvsMD'] = seeds['MAvsMD'][:-24]
            seeds['sqrt.r'] = seeds['sqrt.r'][:-24]
        seeds['lambdaD'] = seeds['lambdaD'][-100:]
        seeds['MAvsMD'] = seeds['MAvsMD'][-100:]
        seeds['sqrt.r'] = seeds['sqrt.r'][-100:]

        for model_name, model in (('lambdaD', self.lambdaD_model),
                                  ('MAvsMD', self.MAvsMD_model),
                                  ('sqrt.r', self.sqrt_r_model)):
            # ro.r.assign('%s.coef' % model_name, ro.ListVector(model.coef.items()))

            long_command = '%s.model <- list(arma=c(%d,%d,%d,%d,%d,%d,%d), coef=list(%s), sigma2=%f, model=list(phi=c(%s), theta=c(%s)))' % \
                           (model_name, model.p, model.q, model.P, model.Q,
                            model.m, model.d, model.D,
                            ','.join(['%s=%.20f' % (name, value) for name, value in model.coef.iteritems()]),
                            model.sigma2,
                            ','.join(['%.20f' % x for x in model.phi]),
                            ','.join(['%.20f' % x for x in model.theta]),
                            )
            # long_command = '%s.model <- list(arma=c(%d,%d,%d,%d,%d,%d,%d), coef=%s.coef, sigma2=%f)' % \
            #                (model_name, model.p, model.q, model.P, model.Q,
            #                 model.m, model.d, model.D, model_name,
            #                 model.sigma2)
            logging.debug(long_command)
            ro.r(long_command)
            # logging.debug(ro.r('Mod(polyroot(c(1, -%s.model$coef)))' % model_name))
            # logging.debug(ro.r('%s.model' % model_name))
            if model_name == 'lambdaD':
                seed = np.log(np.array(seeds[model_name], dtype=np.float))
            else:
                seed = np.array(seeds[model_name], dtype=np.float)
            ro.r.assign('%s.seed' % model_name, numpy2ri.numpy2ri(seed))
            # ro.r('%s.arima <- Arima(%s.seed, model=%s.model)' % (model_name, model_name, model_name))
            # ro.r('%s.arima <- Arima(rep(0, 48), model=%s.model)' % (model_name, model_name))
            # ro.r('%s.arima$sigma2 = %f' % (model_name, model.sigma2))

        # simulated_lambdaD_s = []
        # simulated_MAvsMD_s = []
        # simulated_sqrt_r_s = []

        simulated_lambdaD = ro.r(
            'arima.condsim(lambdaD.model, lambdaD.seed, %d, %d)' % (time_span * 3, n_da_price_scenarios))
        simulated_lambdaD = numpy2ri.ri2py(simulated_lambdaD).transpose()[:, :time_span]
        simulated_lambdaD = np.exp(simulated_lambdaD)

        simulated_MAvsMD = ro.r(
            'arima.condsim(MAvsMD.model, MAvsMD.seed, %d, %d)' % (time_span * 3, n_da_am_price_scenarios))
        simulated_MAvsMD = numpy2ri.ri2py(simulated_MAvsMD).transpose()[:, :time_span]

        simulated_sqrt_r = ro.r(
            'arima.condsim(sqrt.r.model, sqrt.r.seed, %d, %d)' % (time_span * 3, n_adj_price_scenarios))
        simulated_sqrt_r = numpy2ri.ri2py(simulated_sqrt_r).transpose()[:, :time_span]

        # for sample_num in xrange(n_samples):
        #     simulated_lambdaD = ro.r('simulate.Arima(lambdaD.arima, %d)' % time_span)
        #     simulated_lambdaD = numpy2ri.ri2py(simulated_lambdaD)
        #     simulated_lambdaD = np.exp(simulated_lambdaD)
        #     simulated_lambdaD_s.append(list(simulated_lambdaD))
        #
        #     simulated_MAvsMD = ro.r('simulate.Arima(MAvsMD.arima, %d)' % time_span)
        #     simulated_MAvsMD = numpy2ri.ri2py(simulated_MAvsMD)
        #     simulated_MAvsMD_s.append(list(simulated_MAvsMD))
        #
        #     simulated_sqrt_r = ro.r('simulate.Arima(sqrt.r.arima, %d)' % time_span)
        #     simulated_sqrt_r = numpy2ri.ri2py(simulated_sqrt_r)
        #     simulated_sqrt_r_s.append(list(simulated_sqrt_r))

        return simulated_lambdaD, simulated_MAvsMD, simulated_sqrt_r
