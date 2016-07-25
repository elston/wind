import numpy as np
import pandas as pd

from sarima_fit import PriceModel


def test():
    test_data = load_esios_data()
    plot_esios_data(test_data.data)
    test_data.fit_models()


    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    predict_lambdaD = test_data.lambdaD_model.predict(start=100, end=200, dynamic=True)
    plt.plot(test_data.data.index[:200], test_data.data['lambdaD'][:200])
    plt.plot(predict_lambdaD.index, np.exp(predict_lambdaD), '--')
    plt.title('e.sios $\lambda^D$ prediction')
    plt.show()

    predict_MAvsMD = test_data.MAvsMD_model.predict(start=100, end=200, dynamic=True)
    plt.plot(test_data.data.index[:200], test_data.data['MAvsMD'][:200])
    plt.plot(predict_MAvsMD.index, predict_MAvsMD, '--')
    plt.title('e.sios $\Delta\lambda$ prediction')
    plt.show()

    predict_imbalance = test_data.imbalance_model.predict(start=100, end=200, dynamic=True)
    plt.plot(test_data.data.index[:200], test_data.data['imbalance'][:200])
    plt.plot(predict_imbalance.index, predict_imbalance, '--')
    plt.title('e.sios $\sqrt{r}$ prediction')
    plt.show()


def load_esios_data():
    dataframe = parse_esios_data()
    price_data = PriceModel()
    price_data.data = dataframe
    return price_data


def parse_esios_data():
    with open('../data/esios/export_MarginalPriceDayAheadMarketSpain_2016-07-24_19_35.csv', 'rb') as csvfile:
        lambdaD_df = pd.read_csv(csvfile,
                                 delimiter=';',
                                 header=0,
                                 index_col=1,  # 5th actually
                                 names=['lambdaD', 'time'],
                                 usecols=[4, 5],
                                 parse_dates=True,
                                 infer_datetime_format=True)

    with open('../data/esios/export_MarginalPriceIntradayMarketSession1Spain_2016-07-25_13_29.csv', 'rb') as csvfile:
        lambdaA_df = pd.read_csv(csvfile,
                                 delimiter=';',
                                 header=0,
                                 index_col=1,  # 5th actually
                                 names=['lambdaA', 'time'],
                                 usecols=[4, 5],
                                 parse_dates=True,
                                 infer_datetime_format=True)

    with open('../data/esios/export_UpwardImbalancesCollectionPrice_2016-07-24_19_49.csv', 'rb') as csvfile:
        mixed_data = pd.read_csv(csvfile,
                                 delimiter=';',
                                 header=0,
                                 index_col=2,  # 5th actually
                                 names=['id', 'data', 'time'],
                                 usecols=[0, 4, 5],
                                 parse_dates=True,
                                 infer_datetime_format=True)

    upward_prices = mixed_data[mixed_data.id == 686]  # e.sios specific code
    upward_prices.rename(columns={'data': 'lambdaPlus'}, inplace=True)
    downward_prices = mixed_data[mixed_data.id == 687]  # e.sios specific code
    downward_prices.rename(columns={'data': 'lambdaMinus'}, inplace=True)

    combined_data = lambdaD_df.join(lambdaA_df, how='inner') \
        .join(upward_prices, how='inner') \
        .join(downward_prices, how='inner', rsuffix='_down', sort=True)

    combined_data.drop(['id', 'id_down'], inplace=True, axis=1)

    MAvsMD = combined_data['lambdaA'] - combined_data['lambdaD']
    combined_data = combined_data.assign(MAvsMD=MAvsMD)
    r_neg = combined_data['lambdaMinus'] / combined_data['lambdaD']
    combined_data = combined_data.assign(r_neg=r_neg)
    r_pos = combined_data['lambdaPlus'] / combined_data['lambdaD']
    combined_data = combined_data.assign(r_pos=r_pos)
    imbalance = np.sqrt(combined_data['r_pos'] + combined_data['r_neg'] - 1)
    combined_data = combined_data.assign(imbalance=imbalance)

    return combined_data


def plot_esios_data(dataframe):
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt

    ax1 = plt.subplot(2, 2, 1)
    ax1.plot(dataframe.index, dataframe.lambdaD)
    plt.ylabel('$\lambda^D$')

    ax2 = plt.subplot(2, 2, 2)
    ax2.plot(dataframe.index, dataframe.MAvsMD)
    plt.ylabel('$\Delta\lambda$')

    ax3 = plt.subplot(2, 2, 3)
    ax3.plot(dataframe.index, dataframe.r_neg, label='$r^-$')
    ax3.plot(dataframe.index, dataframe.r_pos, label='$r^+$')
    ax3.legend()
    plt.ylabel('$r^-, r^+$')

    ax4 = plt.subplot(2, 2, 4)
    ax4.plot(dataframe.index, dataframe.imbalance)
    plt.ylabel('$\sqrt{r^+ + r^- - 1}$')

    plt.suptitle('Hourly test data from e.sios (~1 year backwards)')
    plt.show()


if __name__ == '__main__':
    test()
