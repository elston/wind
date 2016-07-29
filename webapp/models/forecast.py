from sqlalchemy.orm import relationship
from webapp import db


class Forecast(db.Model):
    __tablename__ = 'forecasts'

    id = db.Column(db.Integer(), primary_key=True)
    location_id = db.Column(db.Integer(), db.ForeignKey('locations.id'), index=True)
    time = db.Column(db.DateTime(), index=True)  # UTC time

    location = relationship('Location', back_populates='forecasts')
    hourly_forecasts = relationship('HourlyForecast', back_populates='forecast', order_by='HourlyForecast.time',
                                    cascade='all, delete-orphan')
