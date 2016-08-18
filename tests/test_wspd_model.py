# coding=utf-8
import logging
import unittest
from math import sin

import numpy as np
from webapp.models import Location

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class WspdFitTestCase(unittest.TestCase):
    # Sotavento wind farm 2016-05-01 - 2016-05-10, hourly, m/s, 240 values
    sample = [5.14, 5.41, 5.79, 6.45, 5.54, 4.94, 5.63, 6.95, 5.03, 5.50, 6.03, 6.15, 6.24, 5.37, 5.40, 5.64, 5.97,
              6.60, 5.43, 6.26, 8.30, 8.70, 5.79, 5.55, 6.24, 6.84, 7.19, 9.28, 9.32, 8.87, 7.07, 6.55, 5.38, 4.41,
              4.28, 4.51, 4.48, 4.81, 6.26, 6.04, 5.39, 6.23, 4.93, 5.60, 4.43, 4.76, 4.32, 5.02, 8.19, 10.11, 10.72,
              10.14, 10.32, 11.51, 10.30, 10.39, 10.25, 7.79, 8.61, 8.33, 7.22, 7.15, 7.26, 6.58, 7.40, 8.29, 8.71,
              9.91, 9.41, 10.48, 9.63, 7.82, 8.61, 8.74, 9.15, 8.63, 7.73, 6.60, 6.68, 6.90, 7.15, 6.16, 4.73, 4.36,
              4.57, 4.66, 5.74, 7.60, 7.33, 6.95, 6.36, 5.24, 4.27, 4.23, 4.47, 4.16, 4.65, 4.92, 4.90, 4.58, 5.18,
              4.54, 4.47, 4.97, 5.34, 5.18, 5.66, 5.52, 6.01, 5.97, 6.73, 7.32, 6.27, 5.94, 6.02, 4.68, 4.65, 5.35,
              4.37, 3.80, 5.38, 4.66, 4.36, 6.21, 5.25, 4.89, 3.84, 4.28, 2.99, 3.51, 3.75, 4.38, 4.18, 3.57, 3.61,
              3.44, 3.67, 3.08, 2.43, 2.54, 3.00, 3.44, 4.18, 5.30, 8.00, 9.32, 8.95, 8.00, 7.18, 7.37, 5.72, 5.27,
              6.58, 8.32, 10.19, 10.44, 11.54, 11.57, 12.39, 12.90, 11.12, 11.24, 11.26, 12.53, 13.45, 12.57, 7.81,
              6.17, 7.60, 7.29, 6.84, 5.28, 7.39, 8.21, 10.99, 9.97, 12.01, 12.18, 10.72, 10.08, 9.03, 9.11, 9.94, 7.19,
              7.06, 8.52, 10.74, 9.91, 10.71, 9.01, 10.79, 10.46, 9.54, 7.08, 6.54, 6.93, 5.66, 5.72, 5.29, 5.60, 6.55,
              6.07, 6.06, 5.08, 6.22, 9.44, 4.60, 4.26, 5.00, 5.80, 5.28, 5.47, 3.78, 4.70, 4.69, 4.06, 4.43, 4.21,
              4.26, 4.87, 5.62, 7.25, 7.10, 7.16, 7.57, 8.20, 9.59, 8.57, 6.70, 4.00, 3.71, 4.17, 4.68, 3.47, 3.62,
              4.39, 4.53, 4.02, 4.21, 6.10]
    # result from R library MASS function fitdistr(x, "weibull")
    #      shape       scale
    #   3.0047557   7.4723230


    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test(self):
        shape, scale, histogram, pdf, z_histogram, z_pdf, wind_model = Location._fit_get_wspd_model(self.sample)

        # print histogram
        # print pdf
        #
        # import matplotlib
        # matplotlib.use('TkAgg')
        # import matplotlib.pyplot as plt
        # plt.bar([x[0] for x in histogram], [x[1] for x in histogram], align='center')
        # plt.plot([x[0] for x in pdf], [x[1] for x in pdf])
        # plt.show()

        self.assertAlmostEqual(shape, 3.0047557, 4)
        self.assertAlmostEqual(scale, 7.4723230, 4)

if __name__ == '__main__':
    unittest.main()
