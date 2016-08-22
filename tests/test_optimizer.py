# coding=utf-8
import logging
import unittest

from webapp.optimizer import Optimizer
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class ReduceTestCase(unittest.TestCase):
    def test_1(self):
        windpark_id = 2
        optimizer = Optimizer(windpark_id)
        result = optimizer.optimize()
        result.print_output()


if __name__ == '__main__':
    unittest.main()
