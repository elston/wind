from datetime import datetime, timedelta

from sqlalchemy.orm import relationship
from webapp import db, wuclient


class Location(db.Model):
    __tablename__ = 'locations'

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
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

    def download(self, date, today):
        dls = self.get_download_status(date)
        if dls is not None and dls.full:
            return
        data = wuclient.history(date, self.l)
        observations = data['history']['observations']
        for obs_data in observations:
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
            obs = Observation(time=timestamp, tempm=tempm, wspdm=wspdm, wdird=wdird)
            self.observations.append(obs)
        if dls is None:
            dls = HistoryDownloadStatus(date=date, partial=True, full=not today)
            self.history_downloads.append(dls)
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
        forecast = Forecast(location_id=self.id, time=now)
        db.session.add(forecast)
        db.session.flush()
        db.session.refresh(forecast)
        for hourly_data in data['hourly_forecast']:
            ts = int(hourly_data['FCTTIME']['epoch'])
            time = datetime.utcfromtimestamp(ts)
            tempm = float(hourly_data['temp']['metric'])
            wspdm = float(hourly_data['wspd']['metric'])
            wdird = int(hourly_data['wdir']['degrees'])
            hourly_forecast = HourlyForecast(forecast_id=forecast.id, time=time, tempm=tempm,
                                             wspdm=wspdm, wdird=wdird)
            forecast.hourly_forecasts.append(hourly_forecast)
        db.session.commit()


class HistoryDownloadStatus(db.Model):
    __tablename__ = 'history_download_status'

    id = db.Column(db.Integer(), primary_key=True)
    location_id = db.Column(db.Integer(), db.ForeignKey('locations.id'))
    date = db.Column(db.Date())  # UTC date
    partial = db.Column(db.Boolean())
    full = db.Column(db.Boolean())

    location = relationship('Location', back_populates='history_downloads')


class Observation(db.Model):
    __tablename__ = 'observations'

    id = db.Column(db.Integer(), primary_key=True)
    location_id = db.Column(db.Integer(), db.ForeignKey('locations.id'))
    time = db.Column(db.DateTime())  # UTC time
    tempm = db.Column(db.Float())  # Temp in C
    wspdm = db.Column(db.Float())  # WindSpeed kph
    wdird = db.Column(db.Integer())  # Wind direction in degrees

    location = relationship('Location', back_populates='observations')

    def __str__(self):
        return '<Observation id=%s %s temp=%f wspdm=%f wdird=%f>' % (self.id, self.time, self.tempm, self.wspdm,
                                                                     self.wdird)

    @classmethod
    def from_excess_args(cls, **kwargs):
        d = {}
        for c in cls.__table__.columns:
            d[c.name] = kwargs.get(c.name)
        item = Observation(**d)
        return item

    def to_dict(self):
        d = {}
        for c in self.__table__.columns:
            d[c.name] = getattr(self, c.name)
        return d


class Forecast(db.Model):
    __tablename__ = 'forecasts'

    id = db.Column(db.Integer(), primary_key=True)
    location_id = db.Column(db.Integer(), db.ForeignKey('locations.id'), index=True)
    time = db.Column(db.DateTime(), index=True)  # UTC time

    location = relationship('Location', back_populates='forecasts')
    hourly_forecasts = relationship('HourlyForecast', back_populates='forecast', order_by='HourlyForecast.time',
                                    cascade='all, delete-orphan')


class HourlyForecast(db.Model):
    __tablename__ = 'hourly_forecasts'

    id = db.Column(db.Integer(), primary_key=True)
    forecast_id = db.Column(db.Integer(), db.ForeignKey('forecasts.id'), index=True)
    time = db.Column(db.DateTime(), index=True)  # UTC time
    tempm = db.Column(db.Float())  # Temp in C
    wspdm = db.Column(db.Float())  # WindSpeed kph
    wdird = db.Column(db.Integer())  # Wind direction in degrees

    forecast = relationship('Forecast', back_populates='hourly_forecasts')
