# coding=utf-8
import logging
import unittest

from flask import json
import webapp
import re
from webapp.models import Windpark, Turbine
from webapp.models.windpark_turbines import WindparkTurbine

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

user_id = 1
test_name = 'Test windpark'


# TODO: test adding API

class WindparksTestCase(unittest.TestCase):
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
        for market in self.session.query(Windpark).filter_by(name=test_name).all():
            self.session.delete(market)
        self.session.commit()

    def test_add_windpark_int(self):
        test_windpark = Windpark(user_id=user_id, name=test_name)
        self.session.add(test_windpark)
        self.session.commit()
        windpark_id = test_windpark.id
        test_windpark_1 = self.session.query(Windpark).filter_by(id=windpark_id).first()
        self.assertEqual(test_windpark.id, test_windpark_1.id)
        self.assertEqual(test_windpark.user_id, test_windpark_1.user_id)
        self.assertEqual(test_windpark.name, test_windpark_1.name)

    def test_add_windpark_api(self):
        test_windpark = Windpark(user_id=user_id, name=test_name)
        self.session.add(test_windpark)
        self.session.commit()
        windpark_id = test_windpark.id

        rv = self.app.get('/api/windparks')
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data
        test_windpark = [x for x in data if x['name'] == test_name]
        self.assertEqual(1, len(test_windpark))

    def test_add_turbine_to_windpark_int(self):
        test_windpark = Windpark(user_id=user_id, name=test_name)
        self.session.add(test_windpark)
        self.session.commit()
        windpark_id = test_windpark.id

        first_turbine = self.session.query(Turbine).first()
        rel = WindparkTurbine(windpark_id=windpark_id, turbine_id=first_turbine.id, count=1)
        # self.session.add(rel)
        test_windpark.turbines.append(rel)
        self.session.commit()

        rv = self.app.get('/api/windparks')
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data
        test_windpark = [x for x in data if x['name'] == test_name][0]
        turbines = test_windpark['turbines']
        self.assertEqual(turbines[0]['count'], 1)
        self.assertEqual(turbines[0]['turbine_id'], 1)
        self.assertEqual(len(turbines), 1)

    def test_add_turbine_to_windpark_api(self):
        test_windpark = Windpark(user_id=user_id, name=test_name)
        self.session.add(test_windpark)
        self.session.commit()
        windpark_id = test_windpark.id

        rv = self.app.post('/api/windparks/%d/turbines' % windpark_id,
                           data=json.dumps({'count': 1, 'turbine_id': 1}),
                           content_type='application/json')
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)

        rv = self.app.get('/api/windparks')
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data
        test_windpark = [x for x in data if x['name'] == test_name][0]
        turbines = test_windpark['turbines']
        self.assertEqual(turbines[0]['count'], 1)
        self.assertEqual(turbines[0]['turbine_id'], 1)
        self.assertEqual(len(turbines), 1)

    def test_delete_turbine(self):
        test_windpark = Windpark(user_id=user_id, name=test_name)
        self.session.add(test_windpark)
        self.session.commit()
        windpark_id = test_windpark.id

        first_turbine = self.session.query(Turbine).first()
        rel = WindparkTurbine(windpark_id=windpark_id, turbine_id=first_turbine.id, count=1)
        test_windpark.turbines.append(rel)
        self.session.commit()

        rv = self.app.delete('/api/windparks/%d/turbines/%d' % (windpark_id, rel.id))
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)

        rv = self.app.get('/api/windparks')
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data
        test_windpark = [x for x in data if x['name'] == test_name][0]
        turbines = test_windpark['turbines']
        self.assertEqual(len(turbines), 0)


if __name__ == '__main__':
    unittest.main()
