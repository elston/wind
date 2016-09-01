from sqlalchemy.orm import relationship
from webapp import db


class Observation(db.Model):
    __tablename__ = 'observations'

    id = db.Column(db.Integer(), primary_key=True)
    location_id = db.Column(db.Integer(), db.ForeignKey('locations.id'), index=True)
    time = db.Column(db.DateTime(), index=True)  # UTC time
    tempm_raw = db.Column(db.Float())  # Temp in C
    tempm = db.Column(db.Float())  # Temp in C with outliers filtered
    wspdm_raw = db.Column(db.Float())  # WindSpeed kph
    wspdm = db.Column(db.Float())  # WindSpeed kph with outliers filtered
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
