# coding=utf-8
import unittest
import numpy as np
from webapp.api.math.reduce_scenarios import reduce_scenarios, scenarios_distance, get_cost_matrix


class ReduceTestCase(unittest.TestCase):
    scenarios = np.array([[5], [40], [60], [100]], dtype=np.float)
    probabilities = np.array([0.25, 0.2, 0.2, 0.35], dtype=np.float)

    def test_cost(self):
        dist = scenarios_distance(np.array([5]), np.array([40]))
        self.assertAlmostEqual(dist, 35.0)

    def test_cost_martix(self):
        cost_matrix = get_cost_matrix(self.scenarios)
        self.assertListEqual(cost_matrix.tolist(), [[0., 35., 55., 95.],
                                                    [35., 0., 20., 60.],
                                                    [55., 20., 0., 40.],
                                                    [95., 60., 40., 0.]])

    def test_reduce(self):
        new_scenarios, new_probabilities, idxs = reduce_scenarios(self.scenarios, self.probabilities, 2)

        self.assertEqual(new_scenarios.shape, (2, 1))
        self.assertAlmostEqual(new_scenarios[0][0], 60.0)
        self.assertAlmostEqual(new_scenarios[1][0], 100.0)
        self.assertEqual(new_probabilities.shape, (2,))
        self.assertAlmostEqual(new_probabilities[0], 0.65)
        self.assertAlmostEqual(new_probabilities[1], 0.35)
        self.assertEqual(len(idxs), 2)
        self.assertEqual(idxs[0], 2)
        self.assertEqual(idxs[1], 3)

    def test_reduce_big(self):
        n_scenarios = 1000
        n_new_scenarios = 30
        new_scenarios, new_probabilities, idxs = reduce_scenarios(np.random.rand(n_scenarios, 24),
                                                            np.ones(n_scenarios) / n_scenarios,
                                                            n_new_scenarios)

        self.assertEqual(new_scenarios.shape, (n_new_scenarios, 24))
        self.assertAlmostEqual(np.sum(new_probabilities), 1)


if __name__ == '__main__':
    unittest.main()
