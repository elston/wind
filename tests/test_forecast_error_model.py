# coding=utf-8
from datetime import datetime
import logging
import unittest

import webapp
import re
from webapp.models import Location

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

user_id = 1
loc_id = 2


class LocationsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = webapp.app.test_client()
        self.session = webapp.db.session()
        rv = self.app.get('/login', follow_redirects=True)
        mo = re.search(r'name="csrf_token" type="hidden" value="([0-9]+##[0-9a-f]+)"', rv.data)
        token = mo.group(1)
        rv = self.app.post('/login',
                           follow_redirects=True,
                           data={'csrf_token': token,
                                 'email': 'admin',
                                 'password': 'password'})

    def tearDown(self):
        pass

    def test_get_forecast_error_chunked(self):
        location = self.session.query(Location).filter_by(id=loc_id).first()

        errors_chunked = location.errors_chunked()
        self.assertIsInstance(errors_chunked, list)
        chunk0 = errors_chunked[0]
        self.assertIsInstance(chunk0, dict)
        self.assertIsInstance(chunk0['timestamp'], datetime)
        self.assertIsInstance(chunk0['errors'], list)
        error0 = chunk0['errors'][0]
        self.assertIsInstance(error0, list)
        self.assertIsInstance(error0[0], datetime)
        self.assertIsInstance(error0[1], float)
        self.assertEqual(len(error0), 2)

    def test_get_forecast_error_merged(self):
        location = self.session.query(Location).filter_by(id=loc_id).first()

        errors_merged = location.errors_merged()
        self.assertIsInstance(errors_merged, list)
        for i in xrange(len(errors_merged) / 72):
            for j in xrange(36):
                self.assertIsNotNone(errors_merged[i * 72 + j])
                self.assertIsNone(errors_merged[i * 72 + j + 36])

    def test_fit_forecast_error_model(self):
        location = self.session.query(Location).filter_by(id=loc_id).first()

        location.fit_error_model()
        pass


if __name__ == '__main__':
    unittest.main()
