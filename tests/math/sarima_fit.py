import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX


class PriceData(object):
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
        self.lambdaD_model = mod.fit()
        print self.lambdaD_model.summary()

    def fit_MAvsMD(self):
        mod = SARIMAX(self.data.MAvsMD, order=(1, 0, 11), seasonal_order=(1, 0, 1, 24))
        self.MAvsMD_model = mod.fit()
        print self.MAvsMD_model.summary()

    def fit_imbalance(self):
        mod = SARIMAX(self.data.imbalance, order=(2, 0, 1), seasonal_order=(1, 0, 1, 24), enforce_stationarity=False)
        self.imbalance_model = mod.fit(maxiter=200)
        print self.imbalance_model.summary()


def test():
    test_data = load_test_data()
    test_data.fit_models()

    # predict = test_data.lambdaD_model.predict(start=50, end=100)

    # import matplotlib
    # matplotlib.use('TkAgg')
    # import matplotlib.pyplot as plt
    # plt.plot(test_data.data.index[:100], test_data.data['lambdaD'][:100], predict.index, np.exp(predict), '--')
    # plt.show()


def load_test_data():
    price_data = PriceData()
    with open('Historical data.csv', 'rb') as csvfile:
        data = pd.read_csv(csvfile,
                           header=0,
                           index_col=0,
                           names=['time', 'lambdaD', 'MAvsMD', 'imbalance'],
                           parse_dates=True, infer_datetime_format=True)

    price_data.data = data
    # data['lambdaD'].plot(figsize=(12, 8))

    return price_data


if __name__ == '__main__':
    test()
