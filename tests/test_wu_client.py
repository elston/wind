from datetime import date
import logging
import unittest
import time

from webapp import WuClient

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class WuClientTestCase(unittest.TestCase):
    def setUp(self):
        self.wu_client = WuClient()

    def tearDown(self):
        pass

    def test_throttle(self):
        WuClient.min_interval_sec = 0.21
        start1 = time.time()
        self.wu_client.throttle()
        time.sleep(0.15)
        self.wu_client.throttle()
        end = time.time()
        self.assertAlmostEqual(end - start1, 0.21, 2)

    def test_geolookup_single(self):
        data = self.wu_client.geolookup(u'Lithuania/Vilnius')
        print data
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data['response'], dict)
        self.assertIsInstance(data['location'], dict)
        first_result = data['location']
        self.assertEqual(first_result['city'], u'Vilnius')
        self.assertEqual(first_result['country_iso3166'], u'LT')

    def test_history(self):
        data = self.wu_client.history(date(year=2016, month=6, day=1), '/q/zmw:00000.1.10400')
        print data
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data['response'], dict)
        self.assertIsInstance(data['history'], dict)
        observations = data['history']['observations']
        self.assertIsInstance(observations, list)
        self.assertIsInstance(observations[0], dict)


if __name__ == '__main__':
    unittest.main()
