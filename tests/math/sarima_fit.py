import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX


class PriceModel(object):
    def __init__(self):
        self.data = None
        self.lambdaD_model = None
        self.MAvsMD_model = None
        self.imbalance_model = None

    def fit_models(self):
        self.fit_lambdaD()
        self.fit_MAvsMD()
        self.fit_imbalance()

    def fit_lambdaD(self):
        mod = SARIMAX(np.log(self.data.lambdaD), order=(2, 0, 1), seasonal_order=(1, 1, 1, 24))
        self.lambdaD_model = mod.fit(maxiter=200)
        print self.lambdaD_model.summary()

    def fit_MAvsMD(self):
        mod = SARIMAX(self.data.MAvsMD, order=(1, 0, 11), seasonal_order=(1, 0, 1, 24))
        self.MAvsMD_model = mod.fit(maxiter=200)
        print self.MAvsMD_model.summary()

    def fit_imbalance(self):
        mod = SARIMAX(self.data.imbalance, order=(2, 0, 1), seasonal_order=(1, 0, 1, 24), enforce_stationarity=False)
        self.imbalance_model = mod.fit(maxiter=200)
        print self.imbalance_model.summary()
