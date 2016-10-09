import calendar
from datetime import datetime

import pytz


def utc_naive_to_ts(dt):
    return calendar.timegm(dt.timetuple()) * 1000.0


def utc_naive_to_shifted_ts(dt, location_tz):
    location_aware = utc_naive_to_location_aware(dt, location_tz)
    return (calendar.timegm(dt.timetuple()) + location_aware.utcoffset().total_seconds()) * 1000.0


def utc_naive_to_location_aware(dt, location_tz):
    return dt.replace(tzinfo=pytz.UTC).astimezone(location_tz)


def utc_naive_to_tz_name(dt, location_tz):
    return utc_naive_to_location_aware(dt, location_tz).strftime('%Z%z')


def shift_ts(ts, location_tz):
    dt = datetime.utcfromtimestamp(ts / 1000.0)
    return utc_naive_to_shifted_ts(dt, location_tz)


def ts_to_tz_name(ts, location_tz):
    return utc_naive_to_tz_name(datetime.utcfromtimestamp(ts / 1000.0), location_tz)
