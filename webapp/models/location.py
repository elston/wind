from datetime import datetime, timedelta
import logging

from scipy import signal
import numpy as np
from scipy import stats
from sqlalchemy.orm import relationship
from webapp import db, wuclient, app
from .observation import Observation
from .history_download_status import HistoryDownloadStatus
from .forecast import Forecast
from .hourly_forecast import HourlyForecast

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
    lookback = db.Column(db.Integer())
    lookforward = db.Column(db.Integer())
    wspd_shape = db.Column(db.Float())  # shape parameter of wind speed Weibull model
    wspd_scale = db.Column(db.Float())  # scale parameter of wind speed Weibull model

    observations = relationship('Observation', back_populates='location', order_by='Observation.time',
                                cascade='all, delete-orphan')
    history_downloads = relationship('HistoryDownloadStatus', back_populates='location',
                                     cascade='all, delete-orphan')
    forecasts = relationship('Forecast', back_populates='location', order_by='Forecast.time',
                             cascade='all, delete-orphan')

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
            d[c.name] = getattr(self, c.name)
        return d

    def update_history(self):
        now = datetime.utcnow().date()
        self.download(now, today=True)
        for delta in xrange(1, self.lookback):
            self.download(now - timedelta(days=delta), today=False)
        self.filter_history()

    def download(self, date, today):
        dls = self.get_download_status(date)
        if dls is not None and dls.full:
            return
        data = wuclient.history(date, self.l)
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
                obs = Observation(location_id=self.id, time=timestamp, tempm=tempm, wspdm_raw=wspdm, wdird=wdird)
                db.session.add(obs)
            except Exception, e:
                logging.warn('Could not parse observation %r: %r', obs_data, e)
        if dls is None:
            dls = HistoryDownloadStatus(date=date, partial=True, full=not today)
            self.history_downloads.append(dls)
        else:
            dls.partial = True
            dls.full = not today
        db.session.flush()
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
            .all()

        wspdm_raw_values = np.array([x.wspdm_raw for x in observations], dtype=np.float)
        threshold = float(app.config['FILTER_THRESHOLD'])
        kernel_size = int(app.config['FILTER_SIZE'])
        wspdm = self._filter_history(wspdm_raw_values, threshold, kernel_size)

        for idx, observation in enumerate(observations):
            db.session.query(Observation) \
                .filter(Observation.location_id == self.id) \
                .filter(Observation.time == observation.time) \
                .update({Observation.wspdm: wspdm[idx]}, synchronize_session=False)
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
            .all()

        wspdm_values = np.array([x.wspdm for x in observations], dtype=np.float)
        wspdm_values = wspdm_values[np.isfinite(wspdm_values)]
        shape, scale, histogram, pdf = self._fit_get_wspd_model(wspdm_values)
        self.wspd_shape = shape
        self.wspd_scale = scale
        db.session.commit()
        return shape, scale, histogram, pdf

    @staticmethod
    def _fit_get_wspd_model(data):
        shape, location, scale = stats.weibull_min.fit(data, floc=0)
        hist, bin_edges = np.histogram(data, bins='auto')
        bin_width = bin_edges[1] - bin_edges[0]
        bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])
        pdf = stats.weibull_min.pdf(bin_centers, shape, location, scale)
        return shape, scale, zip(bin_centers, hist / float(sum(hist)) / bin_width), zip(bin_centers, pdf)
