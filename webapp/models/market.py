import math

import pytz
import numpy as np
from sqlalchemy.orm import relationship
from webapp import db
from .prices import Prices
from .arima_price_model import ArimaPriceModel


class Market(db.Model):
    __tablename__ = 'markets'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), index=True)
    lambdaD_model = db.Column(ArimaPriceModel())
    MAvsMD_model = db.Column(ArimaPriceModel())
    sqrt_r_model = db.Column(ArimaPriceModel())

    prices = relationship('Prices', back_populates='market', order_by='Prices.time',
                          cascade='all, delete-orphan')

    @classmethod
    def from_excess_args(cls, **kwargs):
        d = {}
        for c in cls.__table__.columns:
            d[c.name] = kwargs.get(c.name)
        item = Market(**d)
        return item

    def to_dict(self):
        d = {}
        for c in ('id', 'name', 'user_id'):
            d[c] = getattr(self, c)
        return d

    def add_prices(self, df):
        for ts in df.index:
            prices = db.session.query(Prices).filter_by(market_id=self.id, time=ts).first()
            if prices is None:
                prices = Prices(market_id=self.id, time=ts)
                db.session.add(prices)
            for name in df.columns.values:
                setattr(prices, name, df[name][ts])
        db.session.commit()

    def get_summary(self):
        n_prices = len(self.prices)
        start = self.prices[0].time.replace(tzinfo=pytz.utc)
        end = self.prices[-1].time.replace(tzinfo=pytz.utc)
        result = {'n_prices': n_prices, 'start': start, 'end': end}
        for name in ('lambdaD', 'lambdaA', 'MAvsMD', 'lambdaPlus', 'lambdaMinus', 'r_pos', 'r_neg', 'sqrt_r'):
            values = []
            for price in self.prices:
                values.append(getattr(price, name))
            values = np.array(values, dtype=np.float)
            values = values[np.isfinite(values)]
            value_max = np.max(values) if values.size > 0 else None
            value_min = np.min(values) if values.size > 0 else None
            value_mean = np.mean(values) if values.size > 0 else None
            value_std = np.std(values) if values.size > 0 else None
            result[name] = {'max': value_max,
                            'min': value_min,
                            'mean': value_mean,
                            'std': value_std}
        for name in ('lambdaD_model', 'MAvsMD_model', 'sqrt_r_model'):
            value = getattr(self, name)
            if value is not None:
                value = value.to_dict()
            result[name] = value
        return result

    def calculate_missing_values(self):
        for price in self.prices:
            if price.lambdaD is not None and price.lambdaA is not None and price.MAvsMD is None:
                price.MAvsMD = price.lambdaA - price.lambdaD
            if price.lambdaD is not None and price.lambdaPlus is not None and price.r_pos is None:
                price.r_pos = price.lambdaPlus / price.lambdaD
            if price.lambdaD is not None and price.lambdaMinus is not None and price.r_neg is None:
                price.r_neg = price.lambdaMinus / price.lambdaD
            if price.r_pos is not None and price.r_neg is not None and price.sqrt_r is None:
                price.sqrt_r = math.sqrt(price.r_pos + price.r_neg - 1)

    def fit_price_model(self):
        lambdaD = []
        MAvsMD = []
        sqrt_r = []
        for price in self.prices:
            lambdaD.append(price.lambdaD)
            MAvsMD.append(price.MAvsMD)
            sqrt_r.append(price.sqrt_r)

        lambdaD = np.array(lambdaD, dtype=np.float)
        values = np.log(lambdaD[np.isfinite(lambdaD)])
        self.lambdaD_model = ArimaPriceModel()
        self.lambdaD_model.set_parameters(p=2, d=0, q=1, P=1, D=1, Q=1, m=24)
        self.lambdaD_model.fit(values)

        MAvsMD = np.array(MAvsMD, dtype=np.float)
        MAvsMD = MAvsMD[np.isfinite(MAvsMD)]
        self.MAvsMD_model = ArimaPriceModel()
        self.MAvsMD_model.set_parameters(p=1, d=0, q=11, P=1, D=0, Q=1, m=24)
        self.MAvsMD_model.fit(MAvsMD)

        sqrt_r = np.array(sqrt_r, dtype=np.float)
        sqrt_r = sqrt_r[np.isfinite(sqrt_r)]
        self.sqrt_r_model = ArimaPriceModel()
        self.sqrt_r_model.set_parameters(p=2, d=0, q=1, P=1, D=0, Q=1, m=24)
        self.sqrt_r_model.fit(sqrt_r)
