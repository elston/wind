import logging

import re
from flask import jsonify, request
from flask_login import current_user
from webapp import app, db, wuclient
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
            table_data.append(location.to_dict())

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
        location = Location.from_excess_args(user_id=current_user.id, **values)
        db.session.add(location)
        location.update_history()
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
