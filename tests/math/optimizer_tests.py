import logging
import unittest

import numpy as np
from webapp.api.math.wind_producer_opt import Input, Optimizator

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class OptimizerTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_single_period(self):
        """
        should not crash
        """
        D = 2
        L = 2
        A = 2
        W = 2
        K = 2
        NT = 1

        inp = Input(D=D, L=L, A=A, W=W, K=K, NT=NT,
                    dt=1.0,
                    Pmax=100.0,
                    alfa=0.95,
                    beta=0,
                    P=np.array([[[100], [50]], [[0], [40]]]),
                    lambdaD=np.array([[50], [20]]),
                    MAvsMD=np.array([[-10], [3]]),
                    r_pos=np.array([[1], [0.9]]),
                    r_neg=np.array([[1.5], [1]]),
                    pi=np.array([0.0098, 0.0042, 0.0294, 0.0126, 0.0182, 0.0078, 0.0546, 0.0234, 0.0343, 0.0147,
                                 0.0245, 0.0105, 0.0637, 0.0273, 0.0455, 0.0195, 0.0147, 0.0063, 0.0441, 0.0189,
                                 0.0273, 0.0117, 0.0819, 0.0351, 0.05145, 0.02205, 0.03675, 0.01575, 0.09555, 0.04095,
                                 0.06825, 0.02925]).reshape((D, L, A, W, K))
                    )
        result = Optimizator()(inp)
        print result.inp
        print result.variables
        result.print_output()

    def test_n_same_periods(self):
        """
        should give same results in each period
        :return:
        """
        D = 2
        L = 2
        A = 2
        W = 2
        K = 2
        NT = 3

        inp = Input(D=D, L=L, A=A, W=W, K=K, NT=NT,
                    dt=1.0,
                    Pmax=100.0,
                    alfa=0.95,
                    beta=0,
                    P=np.array([[[100, 100, 100], [50, 50, 50]], [[0, 0, 0], [40, 40, 40]]]),
                    lambdaD=np.array([[50, 50, 50], [20, 20, 20]]),
                    MAvsMD=np.array([[-10, -10, -10], [3, 3, 3]]),
                    r_pos=np.array([[1, 1, 1], [0.9, 0.9, 0.9]]),
                    r_neg=np.array([[1.5, 1.5, 1.5], [1, 1, 1]]),
                    pi=np.array([0.0098, 0.0042, 0.0294, 0.0126, 0.0182, 0.0078, 0.0546, 0.0234, 0.0343, 0.0147,
                                 0.0245, 0.0105, 0.0637, 0.0273, 0.0455, 0.0195, 0.0147, 0.0063, 0.0441, 0.0189,
                                 0.0273, 0.0117, 0.0819, 0.0351, 0.05145, 0.02205, 0.03675, 0.01575, 0.09555, 0.04095,
                                 0.06825, 0.02925]).reshape((D, L, A, W, K))
                    )
        result = Optimizator()(inp)
        print result.inp
        print result.variables
        result.print_output()

        # all Pd(d,t) are equal in t dimension
        for d in xrange(D):
            min_t = np.min(result.variables.Pd[d])
            max_t = np.max(result.variables.Pd[d])
            self.assertAlmostEqual(min_t, max_t, 6)

        # all Pa(d,l,t) are equal in t dimension
        for d in xrange(D):
            for l in xrange(L):
                min_t = np.min(result.variables.Pa[d][l])
                max_t = np.max(result.variables.Pa[d][l])
                self.assertAlmostEqual(min_t, max_t, 6)

        # all desvP(d,l,w,t) are equal in t dimension
        for d in xrange(D):
            for l in xrange(L):
                for w in xrange(W):
                    min_t = np.min(result.variables.desvP[d][l][w])
                    max_t = np.max(result.variables.desvP[d][l][w])
                    self.assertAlmostEqual(min_t, max_t, 6)

        # all desvN(d,l,w,t) are equal in t dimension
        for d in xrange(D):
            for l in xrange(L):
                for w in xrange(W):
                    min_t = np.min(result.variables.desvN[d][l][w])
                    max_t = np.max(result.variables.desvN[d][l][w])
                    self.assertAlmostEqual(min_t, max_t, 6)

    def test_increasing_beta(self):
        """
        for increasing beta: Pd are not-increasing, expected profit is not-increasing
        :return:
        """
        D = 2
        L = 2
        A = 2
        W = 2
        K = 2
        NT = 3

        results = []
        for beta in (0, 0.1, 1, 3, 6):
            inp = Input(D=D, L=L, A=A, W=W, K=K, NT=NT,
                        dt=1.0,
                        Pmax=100.0,
                        alfa=0.95,
                        beta=beta,
                        P=np.array([[[100, 100, 100], [50, 50, 50]], [[0, 0, 0], [40, 40, 40]]]),
                        lambdaD=np.array([[50, 50, 50], [20, 20, 20]]),
                        MAvsMD=np.array([[-10, -10, -10], [3, 3, 3]]),
                        r_pos=np.array([[1, 1, 1], [0.9, 0.9, 0.9]]),
                        r_neg=np.array([[1.5, 1.5, 1.5], [1, 1, 1]]),
                        pi=np.array([0.0098, 0.0042, 0.0294, 0.0126, 0.0182, 0.0078, 0.0546, 0.0234, 0.0343, 0.0147,
                                     0.0245, 0.0105, 0.0637, 0.0273, 0.0455, 0.0195, 0.0147, 0.0063, 0.0441, 0.0189,
                                     0.0273, 0.0117, 0.0819, 0.0351, 0.05145, 0.02205, 0.03675, 0.01575, 0.09555,
                                     0.04095,
                                     0.06825, 0.02925]).reshape((D, L, A, W, K))
                        )
            result = Optimizator()(inp)
            result.print_output()

            results.append(result)

        for d in xrange(D):
            for t in xrange(NT):
                for i in xrange(len(results) - 1):
                    print 'd=%d t=%d Pd=%d %d' % (
                    d, t, results[i].variables.Pd[d][t], results[i + 1].variables.Pd[d][t])
                    self.assertGreaterEqual(results[i].variables.Pd[d][t] + 1e-6, results[i + 1].variables.Pd[d][t])

        for i in xrange(len(results)):
            print results[i].expected_profit()

        for i in xrange(len(results) - 1):
            self.assertGreaterEqual(results[i].expected_profit() + 1e-6, results[i + 1].expected_profit())
