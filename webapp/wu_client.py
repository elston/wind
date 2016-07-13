import logging
import urllib
import time

import requests


class WuClient:
    min_interval_sec = 60.0 / 300

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

    def geolookup(self, query):
        self.throttle()

        url = 'http://api.wunderground.com/api/%s/geolookup/q/%s.json' % (self.wu_api_key,
                                                                          urllib.quote(query.encode('utf-8')))
        r = requests.get(url)
        response = r.json()
        return response

    def history(self, date, location):
        self.throttle()

        date_str = date.strftime('%Y%m%d')
        url = 'http://api.wunderground.com/api/%s/history_%s/%s.json' % (self.wu_api_key,
                                                                         date_str,
                                                                         location)
        r = requests.get(url)
        response = r.json()
        return response
