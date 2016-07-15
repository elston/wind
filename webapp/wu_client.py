import logging
import urllib
import time

import requests


class WuClient:
    min_interval_sec = 60.0 / 10

    def __init__(self):
        self.wu_api_key = None
        try:
            with open('wu_api_key') as f:
                self.wu_api_key = f.read().strip()
        except Exception, e:
            logging.warning('WU API key not found: %s', e)
        self.last_call_time = 0

    def throttle(self):
        time_to_wait = self.last_call_time + self.min_interval_sec - time.time()
        if time_to_wait > 0:
            time.sleep(time_to_wait)
        self.last_call_time = time.time()

    def api_call(self, call, query):
        self.throttle()

        url = 'http://api.wunderground.com/api/%s/%s%s.json' % (self.wu_api_key,
                                                                call,
                                                                urllib.quote(query.encode('utf-8')))
        r = requests.get(url)
        response = r.json()
        return response

    def geolookup(self, query):
        return self.api_call('geolookup', '/q/' + query)

    def history(self, date, location):
        date_str = date.strftime('%Y%m%d')
        return self.api_call('history_' + date_str, location)

    def hourly_forecast(self, location):
        return self.api_call('hourly', location)

    def hourly_forecast_10days(self, location):
        return self.api_call('hourly10day', location)
