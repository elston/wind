import numpy as np
from scipy.odr import Model, Data, ODR


def model_function(B, v):
    v_cutin = B[0]
    v_rated = B[1]
    v_cutout = B[2]
    w_rated = B[3]

    w = np.piecewise(v,
                     [v < v_cutin,
                      np.logical_and(v >= v_cutin, v < v_rated),
                      np.logical_and(v >= v_rated, v < v_cutout),
                      v >= v_cutout],
                     [0,
                      lambda x: w_rated * (x - v_cutin) / (v_rated - v_cutin),
                      w_rated,
                      0])
    return w


def fit(wind, power):
    apriori_wind_std = 4  # WU rounds wind speed to knots
    apriori_power_std = 2  # guess

    model = Model(model_function)
    data = Data(wind, power, wd=1. / np.power(apriori_wind_std, 2), we=1. / np.power(apriori_power_std, 2))
    v_cutin = 12.
    v_rated = 50.
    v_cutout = 90.
    w_rated = np.max(power)

    odr = ODR(data, model, beta0=[v_cutin, v_rated, v_cutout, w_rated])
    output = odr.run()
    return output

