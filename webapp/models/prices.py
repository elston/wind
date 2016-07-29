from sqlalchemy.orm import relationship
from webapp import db


class Prices(db.Model):
    __tablename__ = 'historical_prices'

    id = db.Column(db.Integer(), primary_key=True)
    market_id = db.Column(db.Integer(), db.ForeignKey('markets.id'), index=True)
    time = db.Column(db.DateTime(), index=True)  # UTC time
    lambdaD = db.Column(db.Float())  # DA price
    lambdaA = db.Column(db.Float())  # AM price
    MAvsMD = db.Column(db.Float())  # AM - DA price
    lambdaPlus = db.Column(db.Float())  #
    lambdaMinus = db.Column(db.Float())  #
    r_pos = db.Column(db.Float())  # lambda+ / lambdaD
    r_neg = db.Column(db.Float())  # lambda- / lambdaD
    sqrt_r = db.Column(db.Float())  # sqrt(r+ + r- -1)

    market = relationship('Market', back_populates='prices')
