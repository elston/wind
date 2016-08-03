from sqlalchemy.orm import relationship
from webapp import db


class Windpark(db.Model):
    __tablename__ = 'windparks'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), index=True)
    location_id = db.Column(db.Integer(), db.ForeignKey('locations.id'), index=True)
    market_id = db.Column(db.Integer(), db.ForeignKey('markets.id'))

    location = relationship('Location', back_populates='windparks')
    market = relationship('Market', back_populates='windparks')

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
