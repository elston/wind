from sqlalchemy.orm import relationship
from webapp import db


class WindparkTurbine(db.Model):
    __tablename__ = 'windpark_turbines'

    id = db.Column(db.Integer(), primary_key=True)
    windpark_id = db.Column(db.Integer(), db.ForeignKey('windparks.id'), index=True)
    turbine_id = db.Column(db.Integer(), db.ForeignKey('turbines.id'))
    count = db.Column(db.Integer())

    windpark = relationship('Windpark', back_populates='turbines')
    turbine = relationship('Turbine')
