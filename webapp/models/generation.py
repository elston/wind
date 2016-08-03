from sqlalchemy.orm import relationship
from webapp import db


class Generation(db.Model):
    __tablename__ = 'generation'

    id = db.Column(db.Integer(), primary_key=True)
    windpark_id = db.Column(db.Integer(), db.ForeignKey('windparks.id'), index=True)
    time = db.Column(db.DateTime(), index=True)  # UTC time
    power = db.Column(db.Float())  # power in MW

    windpark = relationship('Windpark', back_populates='generation')

    @classmethod
    def from_excess_args(cls, **kwargs):
        d = {}
        for c in cls.__table__.columns:
            d[c.name] = kwargs.get(c.name)
        item = Generation(**d)
        return item

    def to_dict(self):
        d = {}
        for c in self.__table__.columns:
            d[c.name] = getattr(self, c.name)
        return d
