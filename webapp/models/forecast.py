import cStringIO
import csv

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

    def get_csv(self):
        csv_file = cStringIO.StringIO()
        fields = ['time', 'tempm', 'wspdm', 'wdird']
        writer = csv.writer(csv_file)
        writer.writerow(fields)

        for fc in self.hourly_forecasts:
            writer.writerow((fc.time, fc.tempm, fc.wspdm, fc.wdird))
        return csv_file.getvalue()
