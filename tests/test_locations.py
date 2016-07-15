# coding=utf-8
import logging
import unittest
from urllib import urlencode

from flask import json
import webapp
import re
from webapp.models import Location, HourlyForecast

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

    def test_update_history(self):
        test_location = Location(user_id=user_id, name=test_name, l='/q/zmw:00000.1.10400', lookback=2)
        self.session.add(test_location)
        self.session.commit()

        test_location.update_history()
        self.session.delete(test_location)

    def test_get_history(self):
        test_location = Location(user_id=user_id, name=test_name, l='/q/zmw:00000.1.10400', lookback=2)
        self.session.add(test_location)
        self.session.commit()

        test_location.update_history()

        rv = self.app.get('/api/locations/%d/history' % test_location.id)
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data

        self.assertIsInstance(data, dict)
        self.assertIsInstance(data['tempm'], list)
        self.assertIsInstance(data['wspdm'], list)
        self.assertIsInstance(data['wdird'], list)

        self.session.delete(test_location)

    def test_update_forecast_int(self):
        test_location = Location(user_id=user_id, name=test_name, l='/q/zmw:00000.1.10400', lookback=2)
        self.session.add(test_location)
        self.session.commit()

        test_location.update_forecast()

        test_location_1 = self.session.query(Location).filter_by(id=test_location.id).first()
        forecast_1 = test_location_1.forecasts[0]
        self.assertEqual(len(forecast_1), 240)
        hourly_forecast_1 = forecast_1.hourly_forecasts[0]
        self.assertIsInstance(hourly_forecast_1, HourlyForecast)

        self.session.delete(test_location)

    def test_update_forecast_api(self):
        test_location = Location(user_id=user_id, name=test_name, l='/q/zmw:00000.1.10400', lookback=2)
        self.session.add(test_location)
        self.session.commit()

        rv = self.app.post('/api/locations/%d/update_forecast' % test_location.id)
        result = json.loads(rv.data)
        self.assertNotIn('error', result)
        self.assertEqual(result['data'], 'OK')

    def test_get_forecast(self):
        test_location = Location(user_id=user_id, name=test_name, l='/q/zmw:00000.1.10400', lookback=2)
        self.session.add(test_location)
        self.session.commit()
        test_location.update_forecast()

        rv = self.app.get('/api/locations/%d/forecast' % test_location.id)
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data

        self.assertIsInstance(data, dict)
        self.assertIsInstance(data['tempm'], list)
        self.assertIsInstance(data['wspdm'], list)
        self.assertIsInstance(data['wdird'], list)
        self.assertEqual(len(data['tempm']), 240)
        self.assertEqual(len(data['wspdm']), 240)
        self.assertEqual(len(data['wdird']), 240)

if __name__ == '__main__':
    unittest.main()
