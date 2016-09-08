import logging

from flask import jsonify
from flask_login import current_user
from webapp import app, db
from webapp.models import Turbine

logger = logging.getLogger(__name__)


@app.route('/api/turbines')
def list_turbines():
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        turbines = db.session.query(Turbine)
        table_data = []
        for turbine in turbines:
            table_data.append(turbine.to_dict())

        js = jsonify({'data': table_data})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/turbines/<turbine_id>/powercurve')
def get_power_curve(turbine_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        turbine = db.session.query(Turbine).filter_by(id=turbine_id).first()
        table_data = []
        for point in turbine.power_curve:
            table_data.append([point.wind_speed, point.power / 1000.0])

        js = jsonify({'data': table_data})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js
