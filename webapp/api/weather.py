import calendar
import logging
from datetime import datetime, timedelta
import cStringIO
import zipfile

import numpy as np
import pytz
import re
from flask import jsonify, request, make_response
from flask_login import current_user
from scipy import stats
from sqlalchemy import func
from webapp import app, db, wuclient, sch
from webapp.models import Location, Forecast, HourlyForecast
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)


@app.route('/api/locations')
def get_locations():
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        locations = db.session.query(Location).filter_by(user_id=current_user.id)
        table_data = []
        for location in locations:
            table_data.append(location.to_dict())
            for key in ('history_start', 'history_end'):
                dt = table_data[-1].get(key)
                if dt is None:
                    dt = datetime.utcfromtimestamp(0)
                table_data[-1][key] = calendar.timegm(dt.timetuple()) * 1000.0

        js = jsonify({'data': table_data})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/locations', methods=['POST', ])
def add_locations():
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        values = request.get_json()
        for key in ('history_start', 'history_end'):
            values[key] = datetime.utcfromtimestamp(values.get(key, 0) / 1000.0).replace(hour=0, minute=0, second=0,
                                                                                         microsecond=0)
        if 'id' in values:
            location = db.session.query(Location).filter_by(user_id=current_user.id, id=values['id']).first()
            location.update_from_dict(values)
            db.session.flush()
        else:
            location = Location.from_excess_args(user_id=current_user.id, **values)
            db.session.add(location)
        # location.update_history()
        # location.update_forecast()
        sch.update_weather_schedules()
        db.session.commit()

        js = jsonify({'data': 'OK'})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/locations/<loc_id>', methods=['DELETE', ])
def delete_locations(loc_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        location = db.session.query(Location).filter_by(user_id=current_user.id, id=loc_id).first()
        db.session.delete(location)
        db.session.commit()
        js = jsonify({'data': 'OK'})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/locations/<loc_id>')
def download_weather_data(loc_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        location = db.session.query(Location).filter_by(user_id=current_user.id, id=loc_id).first()

        zip_file = cStringIO.StringIO()
        zipf = zipfile.ZipFile(zip_file, 'w')

        observations_csv = location.get_observations_csv()
        zipf.writestr('observations.csv', observations_csv)

        for forecast in location.forecasts:
            file_name = secure_filename('forecast_' + forecast.time.isoformat() + '.csv')
            forecast_csv = forecast.get_csv()
            zipf.writestr(file_name, forecast_csv)

        zipf.close()
        zip_data = zip_file.getvalue()
        response = make_response(zip_data)
        file_name = secure_filename(location.name + '.zip')
        response.headers["Content-Disposition"] = "attachment; filename=%s" % file_name
        return response
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/locations/geolookup')
def get_location():
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        query = request.values.get('query')
        if re.match(r'-?[0-9.]+, *-?[0-9.]+', query):  # lat, lon pair
            query = re.sub(r' +', '', query)
        else:
            query = re.sub(r', *', '/', query)

        response = wuclient.geolookup(query)
        js = jsonify({'data': response})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/locations/<loc_id>/update_history', methods=['POST', ])
def update_history(loc_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        location = db.session.query(Location).filter_by(id=loc_id).first()
        location.update_history()
        js = jsonify({'data': 'OK'})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/locations/<loc_id>/history')
def get_history(loc_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        location = db.session.query(Location).filter_by(id=loc_id).first()
        result = {'tempm': [], 'wspdm': [], 'wdird': []}
        for obs in location.observations:
            unix_ts = calendar.timegm(obs.time.timetuple())
            for k in result.iterkeys():
                result[k].append([unix_ts * 1000, getattr(obs, k)])
        js = jsonify({'data': result})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/locations/<loc_id>/update_forecast', methods=['POST', ])
def update_forecast(loc_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        location = db.session.query(Location).filter_by(id=loc_id).first()
        location.update_forecast()
        js = jsonify({'data': 'OK'})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/locations/<loc_id>/forecast')
def get_forecast(loc_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        location = db.session.query(Location).filter_by(id=loc_id).first()
        location_tz = pytz.timezone(location.tz_long)
        location_now = location_tz.localize(datetime.now())

        results = {}
        last_forecast_utc = db.session.query(func.max(Forecast.time)).filter(Forecast.location_id == loc_id)[0][0]
        qry = db.session.query(HourlyForecast).filter(
            Forecast.location_id == loc_id,
            Forecast.time == last_forecast_utc,
            HourlyForecast.forecast_id == Forecast.id).order_by(
            HourlyForecast.time)
        result = {'tempm': [], 'wspdm': [], 'wdird': [],
                  'time': last_forecast_utc.replace(tzinfo=pytz.UTC).astimezone(location_tz).strftime(
                      '%d %b %Y %I:%M%p %Z')
                  }
        for obs in qry.all():
            unix_ts = calendar.timegm(obs.time.timetuple())
            for k in ('tempm', 'wspdm', 'wdird'):
                result[k].append([unix_ts * 1000, getattr(obs, k)])
        results['last'] = result

        last_11am_location_tz = location_now.replace(hour=11, minute=0, second=0, microsecond=0)
        if last_11am_location_tz > location_now:
            last_11am_location_tz = last_11am_location_tz - timedelta(days=1)
        last_11am_utc = last_11am_location_tz.astimezone(pytz.UTC)
        from_date = last_11am_utc - timedelta(minutes=10)
        to_date = last_11am_utc + timedelta(minutes=10)
        qry = db.session.query(Forecast.id).filter(
            Forecast.location_id == loc_id,
            Forecast.time > from_date,
            Forecast.time <= to_date)
        forecast_id = qry.first()
        if forecast_id is not None:
            forecast_id = forecast_id[0]
            qry = db.session.query(HourlyForecast).filter(
                HourlyForecast.forecast_id == forecast_id).order_by(
                HourlyForecast.time)
            result = {'tempm': [], 'wspdm': [], 'wdird': [],
                      'time': last_11am_location_tz.strftime('%d %b %Y %I:%M%p %Z')
                      }
            for obs in qry.all():
                unix_ts = calendar.timegm(obs.time.timetuple())
                for k in ('tempm', 'wspdm', 'wdird'):
                    result[k].append([unix_ts * 1000, getattr(obs, k)])
            results['last_11am'] = result

        last_11pm_location_tz = location_now.replace(hour=23, minute=0, second=0, microsecond=0)
        if last_11pm_location_tz > location_now:
            last_11pm_location_tz = last_11pm_location_tz - timedelta(days=1)
        last_11pm_utc = last_11pm_location_tz.astimezone(pytz.UTC)
        from_date = last_11pm_utc - timedelta(minutes=10)
        to_date = last_11pm_utc + timedelta(minutes=10)
        qry = db.session.query(Forecast.id).filter(
            Forecast.location_id == loc_id,
            Forecast.time > from_date,
            Forecast.time <= to_date)
        forecast_id = qry.first()
        if forecast_id is not None:
            forecast_id = forecast_id[0]
            qry = db.session.query(HourlyForecast).filter(
                HourlyForecast.forecast_id == forecast_id).order_by(
                HourlyForecast.time)
            result = {'tempm': [], 'wspdm': [], 'wdird': [],
                      'time': last_11pm_location_tz.strftime('%d %b %Y %I:%M%p %Z')
                      }
            for obs in qry.all():
                unix_ts = calendar.timegm(obs.time.timetuple())
                for k in ('tempm', 'wspdm', 'wdird'):
                    result[k].append([unix_ts * 1000, getattr(obs, k)])
            results['last_11pm'] = result

        js = jsonify({'data': results})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/locations/<loc_id>/wspd_distr', methods=['POST', ])
def fit_get_wspd_model(loc_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        location = db.session.query(Location).filter_by(id=loc_id).first()
        result = location.fit_get_wspd_model()
        js = jsonify({'data': result})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/locations/<loc_id>/errors_chunked')
def get_errors_chunked(loc_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        location = db.session.query(Location).filter_by(id=loc_id).first()
        result = location.errors_chunked()
        if len(result) == 0:
            raise Exception('No forecasts overlapping with observations within last 30 days')
        start_time = result[0]['timestamp']
        end_time = result[-1]['timestamp'] + timedelta(hours=36)
        for chunk in result:
            chunk['timestamp'] = calendar.timegm(chunk['timestamp'].timetuple()) * 1000.0
            for point in chunk['errors']:
                point[0] = calendar.timegm(point[0].timetuple()) * 1000.0
            for point in chunk['forecasts']:
                point[0] = calendar.timegm(point[0].timetuple()) * 1000.0
        observations = []
        for obs in location.observations:
            if obs.time < start_time or obs.time > end_time:
                continue
            unix_ts = calendar.timegm(obs.time.timetuple())
            observations.append([unix_ts * 1000, obs.wspdm])
        js = jsonify({'data': {'observations': observations, 'errors': result}})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/locations/<loc_id>/errors_merged')
def get_errors_merged(loc_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        location = db.session.query(Location).filter_by(id=loc_id).first()
        errors = location.errors_merged()
        if len(errors) == 0:
            raise Exception('No forecasts overlapping with observations within last 30 days')
        x = np.array(errors, dtype=np.float)
        min = np.nanmin(x)
        max = np.nanmax(x)
        mean = np.nanmean(x)
        std = np.nanstd(x)
        js = jsonify({'data': {'min': min, 'max': max, 'mean': mean, 'std': std, 'errors': errors}})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/locations/<loc_id>/fit_error_model', methods=['POST', ])
def fit_error_model(loc_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        location = db.session.query(Location).filter_by(id=loc_id).first()
        result = location.fit_error_model()
        db.session.commit()
        js = jsonify({'data': result})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/locations/<loc_id>/model_data')
def get_model_data(loc_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        location = db.session.query(Location).filter_by(id=loc_id).first()
        result = location.to_dict()

        if location.forecast_error_model is not None:
            residuals = location.forecast_error_model.residuals
            residuals = [x for x in residuals if not np.isnan(x)]
            (osm, osr), (slope, intercept, r2) = stats.probplot(residuals, dist='norm', fit=True)
            qqplot_data = {'x': list(osm),
                           'y': list(osr),
                           'slope': slope,
                           'intercept': intercept,
                           'r2': r2}

            result['forecast_error_model']['qqplot_data'] = qqplot_data
        js = jsonify({'data': result})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js
