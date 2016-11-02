import logging
import threading
import urllib
import time
from datetime import datetime, timedelta

import pytz
from webapp import db, app
import requests


class WUDailyCount(db.Model):
    __tablename__ = 'wu_daily_count'

    id = db.Column(db.Integer(), primary_key=True)
    count = db.Column(db.Integer())


class WeatherUndergroundLimitError(Exception):
    pass


class WuClient:
    us_eastern_noon = datetime(year=1970, month=1, day=1, tzinfo=pytz.timezone('US/Eastern'))

    def __init__(self):

        self.minute_limit = int(app.config['WU_MINUTE_LIMIT'])
        self.day_limit = int(app.config['WU_DAY_LIMIT'])
        self.min_interval_sec = 60.0 / self.minute_limit

        self.wu_api_key = None
        try:
            with open('wu_api_key') as f:
                self.wu_api_key = f.read().strip()
        except Exception, e:
            logging.warning('WU API key not found: %s', e)
        self.last_call_time = 0
        self.lock = threading.RLock()

    def throttle_minute_(self):
        time_to_wait = self.last_call_time + self.min_interval_sec - time.time()
        if time_to_wait > 0:
            time.sleep(time_to_wait)
        self.last_call_time = time.time()

    def check_day_limit_(self):
        now = datetime.now(tz=pytz.timezone('US/Eastern'))
        day_key = (now - self.us_eastern_noon).days
        db.session.commit()
        counter = db.session.query(WUDailyCount).filter_by(id=day_key).first()
        if counter is None:
            try:
                db.session.add(WUDailyCount(id=day_key, count=1))
                db.session.commit()
            except Exception, e:
                db.session.rollback()
                logging.error(e)
        else:
            if counter.count >= self.day_limit:
                dt = self.us_eastern_noon + timedelta(days=day_key + 1)
                delta = dt - now
                hours, remainder = divmod(delta.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                raise WeatherUndergroundLimitError(
                    'The feature will be unavailable %d hours %d minutes due to limited resources'
                    % (hours, minutes))
            else:
                db.session.query(WUDailyCount).filter_by(id=day_key).update({'count': WUDailyCount.count + 1})
                db.session.commit()

    def check_limits(self):
        self.check_day_limit_()
        self.throttle_minute_()

    def api_call_(self, call, query):
        with self.lock:
            self.check_limits()

            url = 'http://api.wunderground.com/api/%s/%s%s.json' % (self.wu_api_key,
                                                                    call,
                                                                    urllib.quote(query.encode('utf-8')))
            r = requests.get(url)
            try:
                response = r.json()
            except Exception, e:
                logging.exception("Cannot parse %s: %r", r.content, e)
                raise e
            return response

    def geolookup(self, query):
        return self.api_call_('geolookup', '/q/' + query)

    def history(self, date, location):
        date_str = date.strftime('%Y%m%d')
        return self.api_call_('history_' + date_str, location)

    def hourly_forecast(self, location):
        return self.api_call_('hourly', location)

    def hourly_forecast_10days(self, location):
        return self.api_call_('hourly10day', location)
