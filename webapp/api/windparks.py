import calendar
import logging

from flask import jsonify, request
from flask_login import current_user
import pandas as pd
from webapp import app, db
from webapp.models import Windpark, Prices

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
                     names=['time', 'lambdaD', 'MAvsMD', 'sqrt_r'],
                     parse_dates=True, infer_datetime_format=True)
    df.index = df.index.tz_localize('UTC')
    return df


def parse_esios_generation(csvfile, subformat):
    if subformat == 'da':
        df = pd.read_csv(csvfile,
                         delimiter=';',
                         header=0,
                         index_col=2,  # 5th actually
                         names=['id', 'lambdaD', 'time'],
                         usecols=[0, 4, 5],
                         parse_dates=True,
                         infer_datetime_format=True)
        if not (df.id == 600).all():
            raise Exception("This file doesn't look like e.sios day ahead generation")
        df.drop(['id'], inplace=True, axis=1)
    elif subformat == 'am':
        df = pd.read_csv(csvfile,
                         delimiter=';',
                         header=0,
                         index_col=2,  # 5th actually
                         names=['id', 'lambdaA', 'time'],
                         usecols=[0, 4, 5],
                         parse_dates=True,
                         infer_datetime_format=True)
        if not (df.id == 612).all():
            raise Exception("This file doesn't look like e.sios intraday generation")
        df.drop(['id'], inplace=True, axis=1)
    elif subformat == 'bal':
        mixed_data = pd.read_csv(csvfile,
                                 delimiter=';',
                                 header=0,
                                 index_col=2,  # 5th actually
                                 names=['id', 'data', 'time'],
                                 usecols=[0, 4, 5],
                                 parse_dates=True,
                                 infer_datetime_format=True)

        upward_generation = mixed_data[mixed_data.id == 686]  # e.sios specific code
        upward_generation.rename(columns={'data': 'lambdaPlus'}, inplace=True)
        downward_generation = mixed_data[mixed_data.id == 687]  # e.sios specific code
        downward_generation.rename(columns={'data': 'lambdaMinus'}, inplace=True)

        df = upward_generation.join(downward_generation, how='inner', rsuffix='_down', sort=True)

        if df.size == 0:
            raise Exception("This file doesn't look like e.sios balancing generation")

        df.drop(['id', 'id_down'], inplace=True, axis=1)
    else:
        raise Exception('Unknown file subformat %s', subformat)

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
        elif file_format.startswith('esios'):
            df = parse_esios_generation(file, file_format.split('-')[1])
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
        elif file_format.startswith('esios'):
            df = parse_esios_generation(file, file_format.split('-')[1])
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


@app.route('/api/windparks/generation/<wpark_id>/<value_name>')
def get_wpark_values(wpark_id, value_name):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        values = db.session.query(Prices.time, getattr(Prices, value_name)) \
            .filter_by(windpark_id=wpark_id) \
            .order_by(Prices.time) \
            .all()

        values = [[calendar.timegm(x[0].utctimetuple()) * 1000, x[1]] for x in values]

        js = jsonify({'data': values})
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
