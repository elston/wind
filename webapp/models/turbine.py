from sqlalchemy.orm import relationship
from webapp import db


class Turbine(db.Model):
    __tablename__ = 'turbines'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    vertical_axis = db.Column(db.Boolean())
    rotor_diameter = db.Column(db.Float())  # m
    rated_power = db.Column(db.Float())  # MW
    v_cutin = db.Column(db.Float())  # m/s
    v_cutoff = db.Column(db.Float())  # m/s
    description = db.Column(db.Unicode())

    power_curve = relationship('TurbinePowerCurve', back_populates='turbine', order_by='TurbinePowerCurve.wind_speed',
                               cascade='all, delete-orphan')

    @classmethod
    def from_excess_args(cls, **kwargs):
        d = {}
        for c in cls.__table__.columns:
            d[c.name] = kwargs.get(c.name)
        item = Turbine(**d)
        return item

    def to_dict(self):
        d = {}
        for c in self.__table__.columns:
            d[c.name] = getattr(self, c.name)
        return d
