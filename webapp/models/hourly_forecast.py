from sqlalchemy.orm import relationship
from webapp import db


class HourlyForecast(db.Model):
    __tablename__ = 'hourly_forecasts'

    id = db.Column(db.Integer(), primary_key=True)
    forecast_id = db.Column(db.Integer(), db.ForeignKey('forecasts.id'), index=True)
    time = db.Column(db.DateTime(), index=True)  # UTC time
    tempm = db.Column(db.Float())  # Temp in C
    wspdm = db.Column(db.Float())  # WindSpeed kph
    wdird = db.Column(db.Integer())  # Wind direction in degrees

    forecast = relationship('Forecast', back_populates='hourly_forecasts')
