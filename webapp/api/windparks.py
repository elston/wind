import calendar
import logging

from flask import jsonify, request
from flask_login import current_user
import numpy as np
import pandas as pd
from webapp import app, db
from webapp.api.math.wind_vs_power_model import fit, model_function
from webapp.models import Windpark, Generation, Observation
from webapp.models.windpark_turbines import WindparkTurbine

logger = logging.getLogger(__name__)


@app.route('/api/windparks')
def list_windparks():
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        windparks = db.session.query(Windpark).filter_by(user_id=current_user.id)
        table_data = []
        for windpark in windparks:
            table_data.append(windpark.to_dict())

        js = jsonify({'data': table_data})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/windparks', methods=['POST', ])
def add_windpark():
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        values = request.get_json()

        if 'id' in values:
            windpark = db.session.query(Windpark).filter_by(user_id=current_user.id, id=values['id']).first()
            windpark.update_from_dict(values)
            db.session.flush()
        else:
            windpark = Windpark.from_excess_args(user_id=current_user.id, **values)
            db.session.add(windpark)
        db.session.commit()

        js = jsonify({'data': 'OK'})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/windparks/<wpark_id>', methods=['DELETE', ])
def delete_windpark(wpark_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        windpark = db.session.query(Windpark).filter_by(user_id=current_user.id, id=wpark_id).first()
        db.session.delete(windpark)
        db.session.commit()
        js = jsonify({'data': 'OK'})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


def parse_custom_generation(csvfile):
    df = pd.read_csv(csvfile,
                     header=0,
                     index_col=0,
                     names=['time', 'power'],
                     parse_dates=True, infer_datetime_format=True)
    df.index = df.index.tz_localize('UTC')
    return df


def parse_sotavento_generation(csvfile):
    dateparse = lambda x: pd.datetime.strptime(x, '%d/%m/%Y %H:%M:%S')
    df = pd.read_csv(csvfile,
                     header=0,
                     index_col=0,
                     names=['time', 'power'],
                     usecols=[0, 3],
                     parse_dates=['time'],
                     date_parser=dateparse)
    df.power /= 1000.0
    df.index = df.index.tz_localize('UTC')
    return df


@app.route('/api/windparks/preview_generation', methods=['POST', ])
def preview_generation():
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        file_format = request.form.get('format')
        file = request.files['file']
        if file_format == 'custom':
            df = parse_custom_generation(file)
        elif file_format == 'sotavento':
            df = parse_sotavento_generation(file)
        else:
            raise Exception('Unknown file format %s', file_format)

        data = {}

        ts_indexes = [calendar.timegm(x.timetuple()) * 1000 for x in df.index]

        for name in df.columns.values:
            data[name] = zip(ts_indexes, df[name])

        js = jsonify({'data': data})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/windparks/generation', methods=['POST', ])
def upload_generation():
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        file_format = request.form.get('format')
        wpark_id = request.form.get('wpark_id')
        file = request.files['file']
        if file_format == 'custom':
            df = parse_custom_generation(file)
        elif file_format == 'sotavento':
            df = parse_sotavento_generation(file)
        else:
            raise Exception('Unknown file format %s', file_format)

        windpark = db.session.query(Windpark).filter_by(id=wpark_id).first()
        windpark.add_generation(df)

        js = jsonify({'data': 'OK'})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/windparks/summary/<wpark_id>')
def wpark_summary(wpark_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        windpark = db.session.query(Windpark).filter_by(id=wpark_id).first()
        data = windpark.get_summary()

        js = jsonify({'data': data})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/windparks/generation/<wpark_id>')
def get_wpark_values(wpark_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        power = db.session.query(Generation.time, Generation.power) \
            .filter_by(windpark_id=wpark_id) \
            .order_by(Generation.time) \
            .all()

        location_id = db.session.query(Windpark.location_id) \
            .filter_by(id=wpark_id) \
            .first()[0]

        wind = db.session.query(Observation.time, Observation.wspdm) \
            .filter_by(location_id=location_id) \
            .order_by(Observation.time) \
            .all()

        values = {'power': [[calendar.timegm(x[0].utctimetuple()) * 1000, x[1]] for x in power],
                  'wind': [[calendar.timegm(x[0].utctimetuple()) * 1000, x[1]] for x in wind]
                  }

        js = jsonify({'data': values})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/windparks/windvspower/<wpark_id>')
def get_wind_vs_power(wpark_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        location_id = db.session.query(Windpark.location_id) \
            .filter_by(id=wpark_id) \
            .first()[0]

        wind_vs_power = db.session.query(Observation.wspdm, Generation.power) \
            .filter(Generation.windpark_id == wpark_id) \
            .filter(Observation.location_id == location_id) \
            .filter(Observation.time == Generation.time) \
            .all()

        wind = np.array([x[0] for x in wind_vs_power])
        power = np.array([x[1] for x in wind_vs_power])

        model = fit(wind, power)

        model_wind = np.linspace(np.min(wind), np.max(wind))
        model_power = model_function(model.beta, model_wind)

        result = {'scatterplot': wind_vs_power,
                  'beta': list(model.beta),
                  'sd_beta': list(model.sd_beta),
                  'model': zip(model_wind, model_power)}

        js = jsonify({'data': result})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/windparks/generation/fit_model/<wpark_id>', methods=['POST', ])
def fit_generation_model(wpark_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        windpark = db.session.query(Windpark).filter_by(id=wpark_id).first()
        windpark.fit_generation_model()
        db.session.commit()

        js = jsonify({'data': 'OK'})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/windparks/<wpark_id>/turbines', methods=['POST', ])
def add_turbine(wpark_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        values = request.get_json()

        windpark = db.session.query(Windpark).filter_by(id=wpark_id).first()
        rel = WindparkTurbine(windpark_id=wpark_id, turbine_id=values['turbine_id'], count=values['count'])
        windpark.turbines.append(rel)
        db.session.commit()

        js = jsonify({'data': 'OK'})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/windparks/<wpark_id>/turbines/<relationship_id>', methods=['DELETE', ])
def delete_turbine(wpark_id, relationship_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        windpark = db.session.query(Windpark).filter_by(id=wpark_id).first()
        for rel in windpark.turbines[:]:
            if rel.id == int(relationship_id):
                windpark.turbines.remove(rel)
        db.session.commit()

        js = jsonify({'data': 'OK'})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/windparks/<wpark_id>/totalpowercurve')
def get_total_power_curve(wpark_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        windpark = db.session.query(Windpark).filter_by(id=wpark_id).first()
        power_curve = windpark.get_total_power_curve()
        js = jsonify({'data': power_curve})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/windparks/simulation/<wpark_id>')
def get_simulation(wpark_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        windpark = db.session.query(Windpark).filter_by(id=wpark_id).first()

        time_span = int(request.values.get('time_span'))
        n_samples = int(request.values.get('n_samples'))

        simulated_wind, simulated_power = windpark.simulate_generation(time_span, n_samples)

        js = jsonify({'data': {'wind_speed': simulated_wind.tolist(), 'power': simulated_power.tolist()}})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js
