import logging
import unittest

import numpy as np
from numpy.testing import assert_allclose
from webapp.api.math.wind_vs_power_model import fit, model_function

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class WindVsPowerTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_model(self):
        v_cutin = 2.0
        v_rated = 3.5
        v_cutout = 7
        w_rated = 3

        B = [v_cutin, v_rated, v_cutout, w_rated]

        v = np.array([0, 1, 2, 3, 3.5, 4, 6, 7, 8])
        expected = np.array([0, 0, 0, 2, 3, 3, 3, 0, 0])

        w = model_function(B, v)
        assert_allclose(w, expected)

    def test_exact_fit(self):
        v = np.array([0.0, 5.0, 10., 20., 30., 40., 50., 70., 90., 99.])
        w = np.array([0.0, 0.0, 0.0, 2.5, 5.0, 7.5, 10., 10., 0.0, 0.0])

        result = fit(v, w)
        print result.beta
        print result.sd_beta

    def test_inexact_fit(self):
        v = np.array([0.0, 5.0, 10., 20., 30., 40., 50., 70., 90., 99.]) + \
            np.array([0, 1, 0, -1, 0, 1, 0, -1, 0, 1]) * 0.5
        w = np.array([0.0, 0.0, 0.0, 2.5, 5.0, 7.5, 10., 10., 0.0, 0.0]) + \
            np.array([1, 0, -1, 0, 1, 0, -1, 0, 1, 0]) * 0.5

        result = fit(v, w)
        print result.beta
        print result.sd_beta
