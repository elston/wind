# coding=utf-8
import logging
import unittest
from math import sin

import numpy as np
from webapp.models import Location

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class OutliersTestCase(unittest.TestCase):
    sample_size = 100
    outliers_indices = (6, 7, 32, 50, 67, 69)
    hole_indices = (40, 42)

    def setUp(self):
        a = 5.  # shape
        np.random.seed(0)
        self.raw_data = np.random.weibull(a, self.sample_size)
        self.expected_min = np.min(self.raw_data)
        self.expected_max = np.max(self.raw_data)
        for i in self.outliers_indices:
            self.raw_data[i] = 10000 * sin(i)
        for i in self.hole_indices:
            self.raw_data[i] = None

    def tearDown(self):
        pass

    def test(self):
        data = Location._filter_history(self.raw_data)

        # import matplotlib
        # matplotlib.use('TkAgg')
        # import matplotlib.pyplot as plt
        # plt.plot(range(self.sample_size), self.raw_data, range(self.sample_size), data)
        # plt.ylim([0, 2])
        # plt.show()

        self.assertEqual(len(data), len(self.raw_data))

        good_data_initial = [self.raw_data[i] for i in xrange(self.sample_size) if i not in self.outliers_indices
                             and i not in self.hole_indices]
        good_data_filtered = [data[i] for i in xrange(self.sample_size) if i not in self.outliers_indices
                              and i not in self.hole_indices]

        self.assertListEqual(good_data_filtered, good_data_initial)

        data_without_nans = data[np.isfinite(data)]

        self.assertTrue(np.all(data_without_nans <= self.expected_max))
        self.assertTrue(np.all(data_without_nans >= self.expected_min))


if __name__ == '__main__':
    unittest.main()
