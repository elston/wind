# coding=utf-8
import logging
import unittest
from flask import json
import webapp
import re

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

user_id = 1


class TurbinesTestCase(unittest.TestCase):
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

    def test_list_turbines(self):
        rv = self.app.get('/api/turbines')
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data
        self.assertGreater(len(data), 100)
        self.assertIsInstance(data[0], dict)
        self.assertIn('rated_power', data[0])
        self.assertIn('v_cutin', data[0])
        self.assertIn('v_cutoff', data[0])
        self.assertIn('rotor_diameter', data[0])
        self.assertIn('name', data[0])

    def test_get_power_curve(self):
        rv = self.app.get('/api/turbines/1/powercurve')
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data
        self.assertIsInstance(data, list)
        for element in data:
            self.assertIsInstance(element, list)
            self.assertEqual(len(element), 2)
            self.assertIsInstance(element[0], float)
            self.assertIsInstance(element[1], float)


if __name__ == '__main__':
    unittest.main()
