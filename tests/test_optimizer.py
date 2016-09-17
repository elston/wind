# coding=utf-8
from time import sleep
import unittest

from webapp import tasks
from webapp.optimizer import Optimizer


class OptimizerTestCase(unittest.TestCase):
    def test_direct(self):
        windpark_id = 1
        optimizer = Optimizer(windpark_id)
        result = optimizer.optimize()
        print result.to_dict()

    def test_rq(self):
        windpark_id = 2
        job = tasks.start_windpark_optimization(windpark_id)
        while True:
            job = tasks.windpark_optimization_status(windpark_id)
            print job.status, job.meta
            if job.is_finished:
                print job.result
            if job.is_failed:
                print job.exc_info
            if job.is_finished or job.is_failed:
                break
            sleep(2)


if __name__ == '__main__':
    unittest.main()
