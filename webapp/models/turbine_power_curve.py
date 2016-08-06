from sqlalchemy.orm import relationship
from webapp import db


class TurbinePowerCurve(db.Model):
    __tablename__ = 'turbine_power_curves'

    id = db.Column(db.Integer(), primary_key=True)
    turbine_id = db.Column(db.Integer(), db.ForeignKey('turbines.id'), index=True)
    wind_speed = db.Column(db.Float)  # m/s
    power = db.Column(db.Float())  # MW

    turbine = relationship('Turbine', back_populates='power_curve')

    @classmethod
    def from_excess_args(cls, **kwargs):
        d = {}
        for c in cls.__table__.columns:
            d[c.name] = kwargs.get(c.name)
        item = TurbinePowerCurve(**d)
        return item

    def to_dict(self):
        d = {}
        for c in self.__table__.columns:
            d[c.name] = getattr(self, c.name)
        return d
