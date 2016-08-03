import calendar
import numpy as np
import pytz
from sqlalchemy.orm import relationship
from webapp import db
from .generation import Generation


class Windpark(db.Model):
    __tablename__ = 'windparks'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), index=True)
    location_id = db.Column(db.Integer(), db.ForeignKey('locations.id'), index=True)
    market_id = db.Column(db.Integer(), db.ForeignKey('markets.id'))

    location = relationship('Location', back_populates='windparks')
    market = relationship('Market', back_populates='windparks')
    generation = relationship('Generation', back_populates='windpark', order_by='Generation.time',
                              cascade='all, delete-orphan')

    @classmethod
    def from_excess_args(cls, **kwargs):
        d = {}
        for c in cls.__table__.columns:
            d[c.name] = kwargs.get(c.name)
        item = Windpark(**d)
        return item

    def to_dict(self):
        d = {}
        for c in ('id', 'name'):
            d[c] = getattr(self, c)
        d['location'] = self.location.name if self.location is not None else None
        d['market'] = self.market.name if self.location is not None else None
        return d

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
