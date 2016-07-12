# coding=utf-8
import logging
import unittest
from urllib import urlencode

from flask import json
import webapp
import re
from webapp.models import Location

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

user_id = 1
test_name = 'Test location'


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
        self.session.query(Location).filter_by(name=test_name).delete()
        self.session.commit()

    def test_add_location_int(self):
        test_location = Location(user_id=user_id, name=test_name)
        self.session.add(test_location)
        self.session.commit()
        location_id = test_location.id
        test_location_1 = self.session.query(Location).filter_by(id=location_id).first()
        self.assertEqual(test_location.id, test_location_1.id)
        self.assertEqual(test_location.user_id, test_location_1.user_id)
        self.assertEqual(test_location.name, test_location_1.name)

    def test_add_location_api(self):
        test_location = Location(user_id=user_id, name=test_name)
        self.session.add(test_location)
        self.session.commit()
        location_id = test_location.id

        rv = self.app.get('/api/locations')
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data
        test_location = [x for x in data if x['name'] == test_name]
        self.assertEqual(1, len(test_location))

    def test_geolookup_not_found(self):
        rv = self.app.get('/api/locations/geolookup?' +
                          urlencode({'query': u'Mighty Jagrafess of the Holy Hadrojassic Maxarodenfoe'.encode('utf8')}))
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data['response'], dict)
        self.assertIsInstance(data['response']['error'], dict)
        self.assertEqual(data['response']['error']['type'], 'querynotfound')

    def test_geolookup_many(self):
        rv = self.app.get('/api/locations/geolookup?' +
                          urlencode({'query': u'Deutschland, Düsseldorf'.encode('utf8')}))
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data['response'], dict)
        self.assertIsInstance(data['response']['results'], list)
        self.assertNotIn('location', data)
        self.assertIsInstance(data['response']['results'][0], dict)
        first_result = data['response']['results'][0]
        self.assertEqual(first_result['city'], u'Düsseldorf')
        self.assertEqual(first_result['country_iso3166'], u'DE')

    def test_geolookup_single(self):
        rv = self.app.get('/api/locations/geolookup?' +
                          urlencode({'query': u'Lithuania, Vilnius'.encode('utf8')}))
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data['response'], dict)
        self.assertIsInstance(data['location'], dict)
        first_result = data['location']
        self.assertEqual(first_result['city'], u'Vilnius')
        self.assertEqual(first_result['country_iso3166'], u'LT')

    def test_geolookup_lat_lon(self):
        rv = self.app.get('/api/locations/geolookup?' +
                          urlencode({'query': u'44.590278, 28.565278'.encode('utf8')}))
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data['response'], dict)
        self.assertIsInstance(data['location'], dict)
        first_result = data['location']
        self.assertEqual(first_result['city'], u'Fântânele')
        self.assertEqual(first_result['country_iso3166'], u'RO')


if __name__ == '__main__':
    unittest.main()
