# coding=utf-8
import logging
from time import sleep
import unittest

import webapp
from webapp.models import Location
from webapp.scheduler import Scheduler, scheduled_forecast_update

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

user_id = 1
test_name = 'Test location'


class SchedulerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = webapp.app
        self.session = webapp.db.session()

    def tearDown(self):
        self.session.query(Location).filter_by(name=test_name).delete()
        self.session.commit()

    def test_update_locations(self):
        test_location = Location(user_id=user_id, name=test_name, l='/q/zmw:00000.1.10400', lookback=2,
                                 time_range='rolling')
        self.session.add(test_location)
        self.session.commit()

        webapp.sch.scheduler.add_job(scheduled_forecast_update, args=(test_location,))
        sleep(10)

if __name__ == '__main__':
    unittest.main()
