# coding=utf-8
import logging
import unittest
from datetime import datetime

from flask import json
import pytz
import webapp
import re
from webapp.models import Market, Prices

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

user_id = 1
test_name = 'Test market'

# TODO: test adding API

class MarketsTestCase(unittest.TestCase):
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
        for market in self.session.query(Market).filter_by(name=test_name).all():
            self.session.delete(market)
        self.session.commit()

    def test_add_market_int(self):
        test_market = Market(user_id=user_id, name=test_name)
        self.session.add(test_market)
        self.session.commit()
        market_id = test_market.id
        test_market_1 = self.session.query(Market).filter_by(id=market_id).first()
        self.assertEqual(test_market.id, test_market_1.id)
        self.assertEqual(test_market.user_id, test_market_1.user_id)
        self.assertEqual(test_market.name, test_market_1.name)

    def test_add_market_api(self):
        test_market = Market(user_id=user_id, name=test_name)
        self.session.add(test_market)
        self.session.commit()
        market_id = test_market.id

        rv = self.app.get('/api/markets')
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data
        test_market = [x for x in data if x['name'] == test_name]
        self.assertEqual(1, len(test_market))

    def test_preview_faked_prices(self):
        test_market = Market(user_id=user_id, name=test_name)
        self.session.add(test_market)
        self.session.commit()

        with open('tests/data/custom_test.csv') as csvfile:
            rv = self.app.post('/api/markets/preview_prices',
                               data={'format': 'custom',
                                     'file': (csvfile, 'test.csv')})
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data
        self.assertEqual(len(data['lambdaD']), 9)
        self.assertEqual(len(data['MAvsMD']), 9)
        self.assertEqual(len(data['sqrt_r']), 9)
        self.assertAlmostEqual(data['lambdaD'][0][1], 27.87, 2)
        self.assertEqual(datetime.utcfromtimestamp(data['lambdaD'][0][0] / 1000).replace(tzinfo=pytz.utc),
                         datetime(year=2015, month=7, day=25, tzinfo=pytz.utc))
        self.assertAlmostEqual(data['lambdaD'][-1][1], 32.79, 2)
        self.assertAlmostEqual(data['MAvsMD'][0][1], -3.69, 2)
        self.assertAlmostEqual(data['MAvsMD'][-1][1], -0.62, 2)
        self.assertAlmostEqual(data['sqrt_r'][0][1], 0.332, 4)
        self.assertAlmostEqual(data['sqrt_r'][-1][1], 1.063, 4)

    def test_upload_faked_prices(self):
        test_market = Market(user_id=user_id, name=test_name)
        self.session.add(test_market)
        self.session.commit()
        market_id = test_market.id

        with open('tests/data/custom_test.csv') as csvfile:
            rv = self.app.post('/api/markets/prices',
                               data={'format': 'custom',
                                     'file': (csvfile, 'test.csv'),
                                     'mkt_id': market_id})
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data

        self.assertEqual(len(test_market.prices), 9)
        self.assertAlmostEqual(test_market.prices[0].lambdaD, 27.87, 2)
        self.assertEqual(test_market.prices[0].time.replace(tzinfo=pytz.utc),
                         datetime(year=2015, month=7, day=25, tzinfo=pytz.utc))
        self.assertAlmostEqual(test_market.prices[-1].lambdaD, 32.79, 2)
        self.assertAlmostEqual(test_market.prices[0].MAvsMD, -3.69, 2)
        self.assertAlmostEqual(test_market.prices[-1].MAvsMD, -0.62, 2)
        self.assertAlmostEqual(test_market.prices[0].sqrt_r, 0.332, 4)
        self.assertAlmostEqual(test_market.prices[-1].sqrt_r, 1.063, 4)

    def test_preview_esios_DA_prices(self):
        test_market = Market(user_id=user_id, name=test_name)
        self.session.add(test_market)
        self.session.commit()

        with open('tests/data/esios/esios_DA_test.csv') as csvfile:
            rv = self.app.post('/api/markets/preview_prices',
                               data={'format': 'esios-da',
                                     'file': (csvfile, 'test.csv')})
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data
        self.assertEqual(len(data['lambdaD']), 9)
        self.assertAlmostEqual(data['lambdaD'][0][1], 64.1, 2)
        self.assertEqual(datetime.utcfromtimestamp(data['lambdaD'][0][0] / 1000).replace(tzinfo=pytz.utc),
                         datetime(year=2015, month=7, day=24, tzinfo=pytz.timezone('Etc/GMT-2')))
        self.assertAlmostEqual(data['lambdaD'][-1][1], 66.22, 2)

    def test_upload_esios_DA_prices(self):
        test_market = Market(user_id=user_id, name=test_name)
        self.session.add(test_market)
        self.session.commit()
        market_id = test_market.id

        with open('tests/data/esios/esios_DA_test.csv') as csvfile:
            rv = self.app.post('/api/markets/prices',
                               data={'format': 'esios-da',
                                     'file': (csvfile, 'test.csv'),
                                     'mkt_id': market_id})
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data

        self.assertEqual(len(test_market.prices), 9)
        self.assertAlmostEqual(test_market.prices[0].lambdaD, 64.1, 2)
        self.assertEqual(test_market.prices[0].time.replace(tzinfo=pytz.utc),
                         datetime(year=2015, month=7, day=24, tzinfo=pytz.timezone('Etc/GMT-2')))
        self.assertAlmostEqual(test_market.prices[-1].lambdaD, 66.22, 2)

    def test_preview_esios_AM_prices(self):
        test_market = Market(user_id=user_id, name=test_name)
        self.session.add(test_market)
        self.session.commit()

        with open('tests/data/esios/esios_AM_test.csv') as csvfile:
            rv = self.app.post('/api/markets/preview_prices',
                               data={'format': 'esios-am',
                                     'file': (csvfile, 'test.csv')})
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data
        self.assertEqual(len(data['lambdaA']), 9)
        self.assertAlmostEqual(data['lambdaA'][0][1], 47.85, 2)
        self.assertEqual(datetime.utcfromtimestamp(data['lambdaA'][0][0] / 1000).replace(tzinfo=pytz.utc),
                         datetime(year=2015, month=7, day=25, tzinfo=pytz.timezone('Etc/GMT-2')))
        self.assertAlmostEqual(data['lambdaA'][-1][1], 44.39, 2)

    def test_upload_esios_AM_prices(self):
        test_market = Market(user_id=user_id, name=test_name)
        self.session.add(test_market)
        self.session.commit()
        market_id = test_market.id

        with open('tests/data/esios/esios_AM_test.csv') as csvfile:
            rv = self.app.post('/api/markets/prices',
                               data={'format': 'esios-am',
                                     'file': (csvfile, 'test.csv'),
                                     'mkt_id': market_id})
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data

        self.assertEqual(len(test_market.prices), 9)
        self.assertAlmostEqual(test_market.prices[0].lambdaA, 47.85, 2)
        self.assertEqual(test_market.prices[0].time.replace(tzinfo=pytz.utc),
                         datetime(year=2015, month=7, day=25, tzinfo=pytz.timezone('Etc/GMT-2')))
        self.assertAlmostEqual(test_market.prices[-1].lambdaA, 44.39, 2)

    def test_preview_esios_balancing_prices(self):
        test_market = Market(user_id=user_id, name=test_name)
        self.session.add(test_market)
        self.session.commit()

        with open('tests/data/esios/esios_bal_test.csv') as csvfile:
            rv = self.app.post('/api/markets/preview_prices',
                               data={'format': 'esios-bal',
                                     'file': (csvfile, 'test.csv')})
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data
        self.assertEqual(len(data['lambdaPlus']), 9)
        self.assertAlmostEqual(data['lambdaPlus'][0][1], 64.1, 2)
        self.assertEqual(datetime.utcfromtimestamp(data['lambdaPlus'][0][0] / 1000).replace(tzinfo=pytz.utc),
                         datetime(year=2015, month=7, day=24, tzinfo=pytz.timezone('Etc/GMT-2')))
        self.assertAlmostEqual(data['lambdaPlus'][-1][1], 66.22, 2)
        self.assertEqual(len(data['lambdaMinus']), 9)
        self.assertAlmostEqual(data['lambdaMinus'][0][1], 72.33, 2)
        self.assertEqual(datetime.utcfromtimestamp(data['lambdaMinus'][0][0] / 1000).replace(tzinfo=pytz.utc),
                         datetime(year=2015, month=7, day=24, tzinfo=pytz.timezone('Etc/GMT-2')))
        self.assertAlmostEqual(data['lambdaMinus'][-1][1], 66.22, 2)

    def test_upload_esios_bal_prices(self):
        test_market = Market(user_id=user_id, name=test_name)
        self.session.add(test_market)
        self.session.commit()
        market_id = test_market.id

        with open('tests/data/esios/esios_bal_test.csv') as csvfile:
            rv = self.app.post('/api/markets/prices',
                               data={'format': 'esios-bal',
                                     'file': (csvfile, 'test.csv'),
                                     'mkt_id': market_id})
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data

        self.assertEqual(len(test_market.prices), 9)
        self.assertAlmostEqual(test_market.prices[0].lambdaPlus, 64.1, 2)
        self.assertEqual(test_market.prices[0].time.replace(tzinfo=pytz.utc),
                         datetime(year=2015, month=7, day=24, tzinfo=pytz.timezone('Etc/GMT-2')))
        self.assertAlmostEqual(test_market.prices[-1].lambdaPlus, 66.22, 2)
        self.assertAlmostEqual(test_market.prices[0].lambdaMinus, 72.33, 2)
        self.assertAlmostEqual(test_market.prices[-1].lambdaMinus, 66.22, 2)

    def test_summary(self):
        test_market = Market(user_id=user_id, name=test_name)
        self.session.add(test_market)
        self.session.commit()
        market_id = test_market.id

        with open('tests/data/custom_test.csv') as csvfile:
            rv = self.app.post('/api/markets/prices',
                               data={'format': 'custom',
                                     'file': (csvfile, 'test.csv'),
                                     'mkt_id': market_id})
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data

        summary = test_market.get_summary()
        print summary
        self.assertEqual(summary['start'], datetime(year=2015, month=7, day=25, tzinfo=pytz.utc))
        self.assertEqual(summary['end'], datetime(year=2015, month=7, day=25, hour=8, tzinfo=pytz.utc))
        self.assertEqual(summary['n_prices'], 9)
        self.assertAlmostEqual(summary['lambdaD']['max'], 32.79, 2)
        self.assertAlmostEqual(summary['lambdaD']['min'], 24.40, 2)
        self.assertAlmostEqual(summary['MAvsMD']['max'], 2.66, 2)
        self.assertAlmostEqual(summary['MAvsMD']['min'], -4.65, 2)
        self.assertAlmostEqual(summary['sqrt_r']['max'], 1.810, 4)
        self.assertAlmostEqual(summary['sqrt_r']['min'], 0.003, 4)

    def test_get_values(self):
        test_market = Market(user_id=user_id, name=test_name)
        self.session.add(test_market)
        self.session.commit()
        market_id = test_market.id

        with open('tests/data/custom_test.csv') as csvfile:
            rv = self.app.post('/api/markets/prices',
                               data={'format': 'custom',
                                     'file': (csvfile, 'test.csv'),
                                     'mkt_id': market_id})
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data

        rv = self.app.get('/api/markets/prices/%d/lambdaD' % market_id)
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data

        self.assertAlmostEqual(data[0][1], 27.87, 2)
        self.assertEqual(datetime.utcfromtimestamp(data[0][0] / 1000).replace(tzinfo=pytz.utc),
                         datetime(year=2015, month=7, day=25, tzinfo=pytz.utc))

    def test_calculate_missing_values_int(self):
        test_market = Market(user_id=user_id, name=test_name)
        self.session.add(test_market)
        self.session.commit()
        market_id = test_market.id

        prices = Prices(lambdaD=1.2, lambdaA=3.2, lambdaPlus=1.1, lambdaMinus=5.4)
        test_market.prices.append(prices)

        test_market.calculate_missing_values()
        self.assertAlmostEqual(test_market.prices[0].MAvsMD, 2.0, 2)
        self.assertAlmostEqual(test_market.prices[0].r_pos, 0.92, 2)
        self.assertAlmostEqual(test_market.prices[0].r_neg, 4.5, 2)
        self.assertAlmostEqual(test_market.prices[0].sqrt_r, 2.10, 2)

    def test_calculate_missing_values_api(self):
        test_market = Market(user_id=user_id, name=test_name)
        self.session.add(test_market)
        self.session.commit()
        market_id = test_market.id

        prices = Prices(lambdaD=1.2, lambdaA=3.2, lambdaPlus=1.1, lambdaMinus=5.4)
        test_market.prices.append(prices)
        self.session.commit()

        rv = self.app.post('/api/markets/prices/calculate_missing/%d' % market_id)
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)

        self.assertAlmostEqual(test_market.prices[0].MAvsMD, 2.0, 2)
        self.assertAlmostEqual(test_market.prices[0].r_pos, 0.92, 2)
        self.assertAlmostEqual(test_market.prices[0].r_neg, 4.5, 2)
        self.assertAlmostEqual(test_market.prices[0].sqrt_r, 2.10, 2)

    def test_fit_models(self):
        test_market = Market(user_id=user_id, name=test_name)
        self.session.add(test_market)
        self.session.commit()
        market_id = test_market.id

        with open('tests/data/custom_test_100.csv') as csvfile:
            rv = self.app.post('/api/markets/prices',
                               data={'format': 'custom',
                                     'file': (csvfile, 'test.csv'),
                                     'mkt_id': market_id})
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data

        test_market.fit_price_model()
        print test_market.lambdaD_model.to_dict()
        print test_market.MAvsMD_model.to_dict()
        print test_market.sqrt_r_model.to_dict()
        self.assertIsNotNone(test_market.lambdaD_model._model)
        self.assertIsNotNone(test_market.MAvsMD_model._model)
        self.assertIsNotNone(test_market.sqrt_r_model._model)

    def test_fit_models_api(self):
        test_market = Market(user_id=user_id, name=test_name)
        self.session.add(test_market)
        self.session.commit()
        market_id = test_market.id

        with open('tests/data/custom_test_100.csv') as csvfile:
            rv = self.app.post('/api/markets/prices',
                               data={'format': 'custom',
                                     'file': (csvfile, 'test.csv'),
                                     'mkt_id': market_id})
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)
        data = result['data']
        print data

        rv = self.app.post('/api/markets/prices/fit_model/%d' % market_id)
        result = json.loads(rv.data)
        self.assertIn('data', result)
        self.assertNotIn('error', result)

        self.session.refresh(test_market)
        self.assertIsNotNone(test_market.lambdaD_model)
        self.assertIsNotNone(test_market.MAvsMD_model)
        self.assertIsNotNone(test_market.sqrt_r_model)
        print test_market.lambdaD_model.to_dict()
        print test_market.MAvsMD_model.to_dict()
        print test_market.sqrt_r_model.to_dict()

        summary = test_market.get_summary()
        print summary

        self.assertIsInstance(summary['lambdaD_model'], dict)
        self.assertIsInstance(summary['MAvsMD_model'], dict)
        self.assertIsInstance(summary['sqrt_r_model'], dict)

if __name__ == '__main__':
    unittest.main()
