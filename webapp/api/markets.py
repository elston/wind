import calendar
import logging

from flask import jsonify, request
from flask_login import current_user
import pandas as pd
from webapp import app, db
from webapp.models import Market

logger = logging.getLogger(__name__)


@app.route('/api/markets')
def get_markets():
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        markets = db.session.query(Market).filter_by(user_id=current_user.id)
        table_data = []
        for market in markets:
            table_data.append(market.to_dict())

        js = jsonify({'data': table_data})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/markets', methods=['POST', ])
def add_markets():
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        values = request.get_json()
        market = Market.from_excess_args(user_id=current_user.id, **values)
        db.session.add(market)
        db.session.commit()

        js = jsonify({'data': 'OK'})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/markets/<mkt_id>', methods=['DELETE', ])
def delete_markets(mkt_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        market = db.session.query(Market).filter_by(user_id=current_user.id, id=mkt_id).first()
        db.session.delete(market)
        db.session.commit()
        js = jsonify({'data': 'OK'})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


def parse_custom_prices(csvfile):
    df = pd.read_csv(csvfile,
                     header=0,
                     index_col=0,
                     names=['time', 'lambdaD', 'MAvsMD', 'sqrt_r'],
                     parse_dates=True, infer_datetime_format=True)
    df.index = df.index.tz_localize('UTC')
    return df


def parse_esios_prices(csvfile, subformat):  # TODO: check esios ids for foolproof
    if subformat == 'da':
        df = pd.read_csv(csvfile,
                         delimiter=';',
                         header=0,
                         index_col=1,  # 5th actually
                         names=['lambdaD', 'time'],
                         usecols=[4, 5],
                         parse_dates=True,
                         infer_datetime_format=True)
    elif subformat == 'am':
        df = pd.read_csv(csvfile,
                         delimiter=';',
                         header=0,
                         index_col=1,  # 5th actually
                         names=['lambdaA', 'time'],
                         usecols=[4, 5],
                         parse_dates=True,
                         infer_datetime_format=True)
    elif subformat == 'bal':
        mixed_data = pd.read_csv(csvfile,
                                 delimiter=';',
                                 header=0,
                                 index_col=2,  # 5th actually
                                 names=['id', 'data', 'time'],
                                 usecols=[0, 4, 5],
                                 parse_dates=True,
                                 infer_datetime_format=True)

        upward_prices = mixed_data[mixed_data.id == 686]  # e.sios specific code
        upward_prices.rename(columns={'data': 'lambdaPlus'}, inplace=True)
        downward_prices = mixed_data[mixed_data.id == 687]  # e.sios specific code
        downward_prices.rename(columns={'data': 'lambdaMinus'}, inplace=True)

        df = upward_prices.join(downward_prices, how='inner', rsuffix='_down', sort=True)

        df.drop(['id', 'id_down'], inplace=True, axis=1)
    else:
        raise Exception('Unknown file subformat %s', subformat)

    df.index = df.index.tz_localize('UTC')
    return df


@app.route('/api/markets/preview_prices', methods=['POST', ])
def preview_prices():
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        file_format = request.form.get('format')
        file = request.files['file']
        if file_format == 'custom':
            df = parse_custom_prices(file)
        elif file_format.startswith('esios'):
            df = parse_esios_prices(file, file_format.split('-')[1])
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


@app.route('/api/markets/prices', methods=['POST', ])
def upload_prices():
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        file_format = request.form.get('format')
        mkt_id = request.form.get('mkt_id')
        file = request.files['file']
        if file_format == 'custom':
            df = parse_custom_prices(file)
        elif file_format.startswith('esios'):
            df = parse_esios_prices(file, file_format.split('-')[1])
        else:
            raise Exception('Unknown file format %s', file_format)

        market = db.session.query(Market).filter_by(id=mkt_id).first()
        market.add_prices(df)

        js = jsonify({'data': 'OK'})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js
