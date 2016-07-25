import pandas as pd

from sarima_fit import PriceModel


def test():
    test_data = load_test_data()
    # test_data.fit_models()

    # predict = test_data.lambdaD_model.predict(start=50, end=100)

    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    # plt.plot(test_data.data.index[:100], test_data.data['lambdaD'][:100], predict.index, np.exp(predict), '--')
    plt.plot(test_data.data.index, test_data.data.lambdaD)
    plt.show()


def load_test_data():
    price_data = PriceModel()

    with open('../data/Historical data.csv', 'rb') as csvfile:
        data = pd.read_csv(csvfile,
                           header=0,
                           index_col=0,
                           names=['time', 'lambdaD', 'MAvsMD', 'imbalance'],
                           parse_dates=True, infer_datetime_format=True)

    price_data.data = data

    return price_data


if __name__ == '__main__':
    test()
