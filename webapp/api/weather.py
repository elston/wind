import logging
import urllib

import re
import requests
from flask import jsonify, request
from flask_login import current_user
from webapp import app, db, wu_api_key
from webapp.models import Location

logger = logging.getLogger(__name__)


@app.route('/api/locations')
def get_locations():
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        locations = db.session.query(Location).filter_by(user_id=current_user.id)
        table_data = []
        for location in locations:
            item = {}
            for k in ['id', 'name', 'country_iso3166', 'country_name', 'city',
                      'tz_short', 'tz_long', 'lat', 'lon', 'l', 'lookback', 'lookforward']:
                item[k] = location.__getattribute__(k)
            table_data.append(item)

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
        values = {'user_id': current_user.id}
        for k in ['name', 'country_iso3166', 'country_name', 'city', 'tz_short', 'tz_long', 'lat', 'lon', 'l',
                  'lookback', 'lookforward']:
            values[k] = request.get_json().get(k)
        location = Location(**values)
        db.session.add(location)
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
        db.session.query(Location).filter_by(user_id=current_user.id, id=loc_id).delete()
        db.session.commit()
        js = jsonify({'data': 'OK'})
        return js
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
        url = 'http://api.wunderground.com/api/%s/geolookup/q/%s.json' % (wu_api_key,
                                                                          urllib.quote(query.encode('utf-8')))
        r = requests.get(url)
        response = r.json()
        js = jsonify({'data': response})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js
