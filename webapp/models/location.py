from collections import defaultdict
import csv
from datetime import datetime, timedelta, time
import logging
import cStringIO

import pytz
from scipy import signal
import numpy as np
from scipy import stats
from sqlalchemy.orm import relationship
import rpy2.robjects as ro
from rpy2.robjects import numpy2ri
from webapp import db, wuclient, app
from .observation import Observation
from .history_download_status import HistoryDownloadStatus
from .forecast import Forecast
from .hourly_forecast import HourlyForecast
from .arima_model import ArimaModel
from webapp.tz_utils import utc_naive_to_ts


class Location(db.Model):
    __tablename__ = 'locations'

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), index=True)
    name = db.Column(db.String(255))
    country_iso3166 = db.Column(db.String(4))  # DE
    country_name = db.Column(db.String(255))  # Germany
    city = db.Column(db.String(255))  # Hagen
    tz_short = db.Column(db.String(10))  # CEST
    tz_long = db.Column(db.String(255))  # Europe/Berlin
    lat = db.Column(db.Float())  # 52.20000076
    lon = db.Column(db.Float())  # 7.98333311
    l = db.Column(db.String(255))  # /q/zmw:00000.14.10317
    time_range = db.Column(db.String(10))
    lookback = db.Column(db.Integer())
    history_start = db.Column(db.DateTime())  # naive UTC
    history_end = db.Column(db.DateTime())  # naive UTC
    lookforward = db.Column(db.Integer())
    wspd_shape = db.Column(db.Float())  # shape parameter of wind speed Weibull model
    wspd_scale = db.Column(db.Float())  # scale parameter of wind speed Weibull model
    wind_model = db.Column(ArimaModel())
    update_at_11am = db.Column(db.Boolean())
    update_at_11pm = db.Column(db.Boolean())
    forecast_error_model = db.Column(ArimaModel())

    observations = relationship('Observation', back_populates='location', order_by='Observation.time',
                                cascade='all, delete-orphan')
    history_downloads = relationship('HistoryDownloadStatus', back_populates='location',
                                     cascade='all, delete-orphan')
    forecasts = relationship('Forecast', back_populates='location', order_by='Forecast.time',
                             cascade='all, delete-orphan')
    windparks = relationship('Windpark', back_populates='location')

    def __str__(self):
        return '<Location id=%s user=%s name=%s city=%s>' % (self.id, self.user_id, self.name, self.city)

    @classmethod
    def from_excess_args(cls, **kwargs):
        d = {}
        for c in cls.__table__.columns:
            d[c.name] = kwargs.get(c.name)
        item = Location(**d)
        return item

    def to_dict(self):
        d = {}
        for c in self.__table__.columns:
            if c.name in ('wind_model', 'forecast_error_model') and getattr(self, c.name) is not None:
                d[c.name] = getattr(self, c.name).to_dict()
            else:
                d[c.name] = getattr(self, c.name)
        d['n_observations'] = len(self.observations)
        return d

    def update_from_dict(self, d):
        for c in self.__table__.columns:
            if c.name in d:
                setattr(self, c.name, d[c.name])

    def update_history(self):
        if self.time_range == 'rolling':
            self.update_rolling_history()
        elif self.time_range == 'fixed':
            self.update_fixed_history()
        else:
            raise Exception('Unsupported value time_range=%r', self.time_range)

    def update_rolling_history(self):
        now = datetime.utcnow().date()
        self.download(now, today=True)
        for delta in xrange(1, self.lookback):
            self.download(now - timedelta(days=delta), today=False)
        self.filter_history()

    def update_fixed_history(self):
        day_count = int((self.history_end - self.history_start).days) + 1
        for single_date in (self.history_start + timedelta(n) for n in range(day_count)):
            self.download(single_date, today=False)
        self.filter_history()

    def download(self, date, today):
        dls = self.get_download_status(date)
        if dls is not None and dls.full:
            return
        data = wuclient.history(date, self.l)
        if ('response' in data and 'error' in data['response']) or 'history' not in data or 'observations' not in data[
            'history']:
            raise Exception('Cannot get observations because of %s', data['response']['error'])

        observations = data['history']['observations']
        for obs_data in observations:
            try:
                utcdate = obs_data['utcdate']
                timestamp = datetime(year=int(utcdate['year']), month=int(utcdate['mon']), day=int(utcdate['mday']),
                                     hour=int(utcdate['hour']), minute=int(utcdate['min']))
                tempm = float(obs_data.get('tempm'))
                wspdm = float(obs_data.get('wspdm'))
                wdird_s = obs_data.get('wdird')
                if wdird_s == '':
                    wdird = 0
                else:
                    wdird = int(wdird_s)
                obs = Observation(location_id=self.id, time=timestamp, tempm_raw=tempm, wspdm_raw=wspdm, wdird=wdird)
                db.session.add(obs)
            except Exception, e:
                logging.warn('Could not parse observation %r: %r', obs_data, e)
        if dls is None:
            dls = HistoryDownloadStatus(location_id=self.id, date=date, partial=True, full=not today)
            db.session.add(dls)
        else:
            dls.partial = True
            dls.full = not today
        db.session.commit()

    def get_download_status(self, date):
        dls = db.session.query(HistoryDownloadStatus). \
            filter(HistoryDownloadStatus.location_id == self.id). \
            filter(HistoryDownloadStatus.date == date). \
            first()
        return dls

    def update_forecast(self):
        now = datetime.utcnow()
        data = wuclient.hourly_forecast_10days(self.l)
        if ('response' in data and 'error' in data['response']) or 'hourly_forecast' not in data:
            raise Exception('Cannot get forecast because of %s', data['response']['error'])

        forecast = Forecast(location_id=self.id, time=now)
        db.session.add(forecast)
        db.session.flush()
        db.session.refresh(forecast)
        for hourly_data in data['hourly_forecast']:
            try:
                ts = int(hourly_data['FCTTIME']['epoch'])
                time = datetime.utcfromtimestamp(ts)
                tempm = float(hourly_data['temp']['metric'])
                wspdm = float(hourly_data['wspd']['metric'])
                wdird = int(hourly_data['wdir']['degrees'])
                hourly_forecast = HourlyForecast(forecast_id=forecast.id, time=time, tempm=tempm,
                                                 wspdm=wspdm, wdird=wdird)
                forecast.hourly_forecasts.append(hourly_forecast)
            except Exception, e:
                logging.warn('Could not parse forecast %r: %r', hourly_data, e)
        db.session.commit()

    def filter_history(self):
        """
        replaces wspdm outliers for last self.lookback observation by median filter product
        """
        observations = db.session.query(Observation) \
            .filter(Observation.location_id == self.id) \
            .order_by(Observation.time) \
            .all()  # TODO: use relationship instead

        threshold = float(app.config['FILTER_THRESHOLD'])
        kernel_size = int(app.config['FILTER_SIZE'])

        wspdm_raw_values = np.array([x.wspdm_raw for x in observations], dtype=np.float)
        wspdm = self._filter_history(wspdm_raw_values, threshold, kernel_size)

        tempm_raw_values = np.array([x.tempm_raw for x in observations], dtype=np.float)
        tempm = self._filter_history(tempm_raw_values, threshold, kernel_size)

        for idx, observation in enumerate(observations):
            try:
                db.session.query(Observation) \
                    .filter(Observation.location_id == self.id) \
                    .filter(Observation.time == observation.time) \
                    .update({Observation.wspdm: wspdm[idx],
                             Observation.tempm: tempm[idx]
                             }, synchronize_session=False)
            except Exception, e:
                logging.error(e)
        db.session.commit()

    @staticmethod
    def _filter_history(raw_data, threshold=3.0, kernel_size=5):
        outlier_flags = np.zeros(raw_data.shape, dtype=bool)
        raw_data = raw_data
        while True:
            mean = np.mean(raw_data[~outlier_flags & np.isfinite(raw_data)])
            std = np.std(raw_data[~outlier_flags & np.isfinite(raw_data)])
            new_outlier_flags = np.abs(raw_data - mean) > threshold * std
            if (new_outlier_flags == outlier_flags).all():
                break
            else:
                outlier_flags = new_outlier_flags
        medfiltered_data = signal.medfilt(raw_data, kernel_size=kernel_size)
        output_data = raw_data.copy()
        for i in outlier_flags.nonzero():
            output_data[i] = medfiltered_data[i]
        return output_data

    def fit_get_wspd_model(self):
        observations = db.session.query(Observation) \
            .filter(Observation.location_id == self.id) \
            .order_by(Observation.time) \
            .all()  # TODO: use relationship instead

        if len(observations) == 0:
            raise Exception('Unable to fit model without data')

        wspdm_collector = defaultdict(list)
        for obs in observations:
            hour = obs.time.replace(minute=0, second=0, microsecond=0)
            wspdm_collector[hour].append(obs.wspdm)

        first_time = min([obs.time for obs in observations])
        last_time = max([obs.time for obs in observations])
        first_hour = first_time.replace(minute=0)
        last_hour = last_time.replace(minute=0)

        wspdm_values = []
        hour = first_hour
        while hour <= last_hour:
            hour_values_list = wspdm_collector[hour]
            if len(hour_values_list) == 0:
                wspdm_values.append(None)
            else:
                wspdm_values.append(sum(hour_values_list) / len(hour_values_list))
            hour += timedelta(hours=1)

        wspdm_values = np.array(wspdm_values, dtype=np.float)
        shape, scale, histogram, pdf, z_histogram, z_pdf, wind_model = self._fit_get_wspd_model(wspdm_values)
        self.wspd_shape = shape
        self.wspd_scale = scale
        self.wind_model = wind_model
        db.session.commit()
        wind_model_dict = wind_model.to_dict()
        wind_model_dict['residuals'] = [x if np.isfinite(x) else None for x in wind_model_dict['residuals']]
        return shape, scale, histogram, pdf, z_histogram, z_pdf, wind_model_dict

    @staticmethod
    def _fit_get_wspd_model(data):
        if isinstance(data, list):
            data = np.array(data, dtype=np.float)
        clean_data = data[np.isfinite(data)]
        shape, location, scale = stats.weibull_min.fit(clean_data, floc=0)
        hist, bin_edges = np.histogram(clean_data, bins=10)
        bin_width = bin_edges[1] - bin_edges[0]
        bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])
        pdf = stats.weibull_min.pdf(bin_centers, shape, location, scale)

        # calculate normalized values (eq 3.5)
        z = stats.norm.ppf(stats.weibull_min.cdf(data, shape, location, scale))
        z[z == -np.inf] = np.nan  # filter out -inf arising from windspeed=0
        z_hist, z_bin_edges = np.histogram(z[np.isfinite(z)], bins=10)
        z_bin_width = z_bin_edges[1] - z_bin_edges[0]
        z_bin_centers = 0.5 * (z_bin_edges[1:] + z_bin_edges[:-1])
        z_pdf = stats.norm.pdf(z_bin_centers, 0, 1)

        wind_model = ArimaModel()
        wind_model.set_parameters(p=2, d=0, q=0, P=0, D=0, Q=0, m=0)
        wind_model.fit(z)

        return (shape,
                scale,
                zip(bin_centers, hist / float(sum(hist)) / bin_width),
                zip(bin_centers, pdf),
                zip(z_bin_centers, z_hist / float(sum(z_hist)) / z_bin_width),
                zip(z_bin_centers, z_pdf),
                wind_model)

    def get_observations_csv(self):
        if self.wind_model is None:
            fields = ['time', 'tempm', 'wspdm', 'wdird']
        else:
            fields = ['time', 'tempm', 'wspdm', 'wdird', 'norm_wspd']
        csv_file = cStringIO.StringIO()
        writer = csv.writer(csv_file)
        writer.writerow(fields)

        for obs in self.observations:
            if self.wind_model is None:
                writer.writerow((obs.time, obs.tempm, obs.wspdm, obs.wdird))
            else:
                writer.writerow((obs.time, obs.tempm, obs.wspdm, obs.wdird,
                                 stats.norm.ppf(stats.weibull_min.cdf(obs.wspdm, self.wspd_shape, 0, self.wspd_scale))))
        return csv_file.getvalue()

    def simulate_wind(self, time_span, n_samples):
        if self.wind_model is None:
            raise Exception('Unable to simulate wind without model')

        long_command = 'wind.model <- list(arma=c(2,0,0,0,0,0,0), coef=list(%s), sigma2=%f, model=list(phi=c(%s), theta=c(%s)))' % \
                       (','.join(['%s=%.20f' % (name, value) for name, value in self.wind_model.coef.iteritems()]),
                        self.wind_model.sigma2,
                        ','.join(['%.20f' % x for x in self.wind_model.phi]),
                        ','.join(['%.20f' % x for x in self.wind_model.theta]),
                        )
        logging.debug(long_command)
        ro.r(long_command)
        seed = np.ones(10) * self.wind_model.coef['intercept']
        ro.r.assign('wind.seed', numpy2ri.numpy2ri(seed))

        simulated_z = ro.r('arima.condsim(wind.model, wind.seed, %d, %d)' % (time_span * 3, n_samples))
        simulated_z = numpy2ri.ri2py(simulated_z).transpose()[:, :time_span]

        simulated_wind = stats.weibull_min.ppf(stats.norm.cdf(simulated_z), self.wspd_shape, 0, self.wspd_scale)

        return simulated_z, simulated_wind

    def simulate_wind_2stage(self, time_span, n_scenarios, da_am_time_span, n_da_am_scenarios):
        if self.wind_model is None:
            raise Exception('Unable to simulate wind without model')

        long_command = 'wind.model <- list(arma=c(2,0,0,0,0,0,0), coef=list(%s), sigma2=%f, model=list(phi=c(%s), theta=c(%s)))' % \
                       (','.join(['%s=%.20f' % (name, value) for name, value in self.wind_model.coef.iteritems()]),
                        self.wind_model.sigma2,
                        ','.join(['%.20f' % x for x in self.wind_model.phi]),
                        ','.join(['%.20f' % x for x in self.wind_model.theta]),
                        )
        logging.debug(long_command)
        ro.r(long_command)
        seed = np.ones(2) * self.wind_model.coef['intercept']
        ro.r.assign('wind.seed.da.am', numpy2ri.numpy2ri(seed))

        simulated_z_da_am = ro.r(
            'arima.condsim(wind.model, wind.seed.da.am, %d, %d)' % (da_am_time_span + 1, n_da_am_scenarios))
        simulated_z_da_am = numpy2ri.ri2py(simulated_z_da_am).transpose()[:, :da_am_time_span]

        simulated_zs = []

        for da_am_z in simulated_z_da_am:
            ro.r.assign('wind.seed', numpy2ri.numpy2ri(da_am_z))
            simulated_z = ro.r('arima.condsim(wind.model, wind.seed, %d, %d)' % (time_span + 1, n_scenarios))
            simulated_z = numpy2ri.ri2py(simulated_z).transpose()[:, :time_span]
            x = np.tile(da_am_z, (simulated_z.shape[0], 1))
            simulated_z = np.concatenate((x, simulated_z), axis=1)
            simulated_zs.append(simulated_z)

        simulated_z = np.array(simulated_zs)

        simulated_wind = stats.weibull_min.ppf(stats.norm.cdf(simulated_z), self.wspd_shape, 0, self.wspd_scale)

        return simulated_z, simulated_wind

    def simulate_wind_with_forecast(self, date, time_span, n_scenarios, da_am_time_span, n_da_am_scenarios,
                                    forecast_error_variance=None):
        if self.forecast_error_model is None:
            raise Exception('Unable to simulate wind without model')

        model = self.forecast_error_model
        if forecast_error_variance is not None:
            var = forecast_error_variance
        else:
            var = model.sigma2
        # p q P Q s d D
        long_command = 'error.model <- list(arma=c(%d,%d,%d,%d,%d,%d,%d), coef=list(%s), sigma2=%f, model=list(phi=c(%s), theta=c(%s)))' % \
                       (model.p, model.q, model.P, model.Q, 0, model.d, model.D,
                        ','.join(['%s=%.20f' % (name, value) for name, value in model.coef.iteritems()]),
                        var,
                        ','.join(['%.20f' % x for x in model.phi]),
                        ','.join(['%.20f' % x for x in model.theta]),
                        )
        logging.debug(long_command)

        location_tz = pytz.timezone(self.tz_long)
        location_12pm = location_tz.localize(datetime.combine(date, time(hour=12))) - timedelta(days=1)
        utc_naive_location_12pm = location_12pm.astimezone(pytz.UTC).replace(tzinfo=None)

        last_forecast = None
        for try_forecast in reversed(self.forecasts):
            if try_forecast.time < utc_naive_location_12pm:
                last_forecast = try_forecast
                break

        if last_forecast is None:
            raise Exception("Not enough forecasts")

        relevant_forecasts = [x for x in last_forecast.hourly_forecasts
                              if utc_naive_location_12pm <= x.time < utc_naive_location_12pm + timedelta(hours=36)]

        if len(relevant_forecasts) < 36:
            raise Exception("Not enough forecasts")

        forecasted_wind = [x.wspdm for x in relevant_forecasts]
        dates = [utc_naive_to_ts(x.time) for x in relevant_forecasts]

        ro.r(long_command)
        seed = np.ones(3) * model.coef['intercept']
        ro.r.assign('error.seed.da.am', numpy2ri.numpy2ri(seed))

        simulated_da_am_error = ro.r(
            'arima.condsim(error.model, error.seed.da.am, %d, %d)' % (da_am_time_span + 2, n_da_am_scenarios))
        simulated_da_am_error = numpy2ri.ri2py(simulated_da_am_error).transpose()[:, :da_am_time_span]

        simulated_errors = []

        for da_am_error in simulated_da_am_error:
            ro.r.assign('error.seed', numpy2ri.numpy2ri(da_am_error))
            simulated_error = ro.r('arima.condsim(error.model, error.seed, %d, %d)' % (time_span + 2, n_scenarios))
            simulated_error = numpy2ri.ri2py(simulated_error).transpose()[:, :time_span]
            x = np.tile(da_am_error, (simulated_error.shape[0], 1))
            simulated_error = np.concatenate((x, simulated_error), axis=1)
            simulated_errors.append(simulated_error)

        simulated_error = np.array(simulated_errors)

        simulated_wind = forecasted_wind + simulated_error

        return forecasted_wind, simulated_wind, dates, last_forecast.time

    def fit_error_model(self):

        if len(self.observations) == 0 or len(self.forecasts) == 0:
            raise Exception('Unable to fit model without data')

        series_to_fit = self.errors_merged()

        series_to_fit = np.array(series_to_fit, dtype=np.float)
        if np.all(np.isnan(series_to_fit)):
            raise Exception('No forecasts overlapping with observations within last 30 days')

        self.forecast_error_model = ArimaModel()
        self.forecast_error_model.set_parameters(p=1, d=0, q=2, P=0, D=0, Q=0, m=0)
        self.forecast_error_model.fit(series_to_fit)

    def errors_merged(self):
        errors_chunked = self.errors_chunked()
        errors_merged = []
        for chunk in errors_chunked:
            for point in chunk['errors']:
                errors_merged.append(point[1])
            errors_merged.extend([None] * 36)
        return errors_merged

    def errors_chunked(self):
        location_tz = pytz.timezone(self.tz_long)
        last_observation_time = self.observations[-1].time.replace(tzinfo=pytz.UTC).astimezone(
            location_tz)  # location aware
        allowed_forecast_time_diff = timedelta(minutes=5)
        forecasts_to_fit = []
        for forecast in self.forecasts:
            forecast_time = forecast.time.replace(tzinfo=pytz.UTC).astimezone(location_tz)  # location aware
            if forecast_time > last_observation_time - timedelta(hours=36):  # too fresh
                continue
            if forecast_time < last_observation_time - timedelta(days=30, hours=36):  # too old
                continue
            if (forecast_time + allowed_forecast_time_diff).time() < time(hour=11,
                                                                          tzinfo=location_tz):  # before 11am - delta
                continue
            if (forecast_time - allowed_forecast_time_diff).time() > time(hour=11, tzinfo=location_tz):
                continue
            if Location.is_close_forecast(forecast, forecasts_to_fit):
                continue
            forecasts_to_fit.append(forecast)

        errors_chunked = []

        logging.info('Using %d forecasts', len(forecasts_to_fit))
        for forecast in forecasts_to_fit:
            logging.info('%s', forecast.time.replace(tzinfo=pytz.UTC).astimezone(location_tz))

            forecast_errors = []
            forecast_data_prepared = []

            qry = db.session.query(HourlyForecast).filter(
                HourlyForecast.forecast_id == forecast.id).order_by(
                HourlyForecast.time)

            forecast_data = qry.all()[:36]
            for forecast_point in forecast_data:

                qry = db.session.query(Observation).filter(
                    Observation.time >= forecast_point.time - timedelta(minutes=30),
                    Observation.time < forecast_point.time + timedelta(minutes=30),
                    Observation.location_id == self.id
                )

                observation_points = qry.all()

                if len(observation_points) == 0:
                    forecast_errors.append([forecast_point.time, None])
                else:
                    average_wspdm = np.average([x.wspdm for x in observation_points])
                    if np.isnan(average_wspdm):
                        forecast_errors.append([forecast_point.time, None])
                    else:
                        error = average_wspdm - forecast_point.wspdm
                        forecast_errors.append([forecast_point.time, error])

                forecast_data_prepared.append([forecast_point.time, forecast_point.wspdm])

            errors_chunked.append(
                {'timestamp': forecast.time, 'errors': forecast_errors, 'forecasts': forecast_data_prepared})

        return errors_chunked

    @staticmethod
    def is_close_forecast(forecast, forecasts_to_fit):
        if len(forecasts_to_fit) == 0:
            return False
        for fut in forecasts_to_fit:
            if abs((forecast.time - fut.time).total_seconds()) < 5 * 60:
                return True
        return False
