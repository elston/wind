import pytz
import numpy as np
from sqlalchemy.orm import relationship
from webapp import db
from .prices import Prices


class Market(db.Model):
    __tablename__ = 'markets'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), index=True)

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
        for c in self.__table__.columns:
            d[c.name] = getattr(self, c.name)
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
        return result
