import calendar
import logging

from flask import jsonify, request, make_response
from flask_login import current_user
import pandas as pd
from webapp import app, db
from webapp.models import Market, Prices
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)


@app.route('/api/markets')
def list_markets():
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
def add_market():
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
def delete_market(mkt_id):
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


@app.route('/api/markets/<mkt_id>')
def download_market_data(mkt_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        market = db.session.query(Market).filter_by(user_id=current_user.id, id=mkt_id).first()
        csv_data = market.get_csv()
        response = make_response(csv_data)
        file_name = secure_filename(market.name + '.csv')
        response.headers["Content-Disposition"] = "attachment; filename=%s" % file_name
        return response
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


def parse_esios_prices(csvfile, subformat):
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
            raise Exception("This file doesn't look like e.sios day ahead prices")
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
            raise Exception("This file doesn't look like e.sios intraday prices")
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

        upward_prices = mixed_data[mixed_data.id == 686]  # e.sios specific code
        upward_prices.rename(columns={'data': 'lambdaPlus'}, inplace=True)
        downward_prices = mixed_data[mixed_data.id == 687]  # e.sios specific code
        downward_prices.rename(columns={'data': 'lambdaMinus'}, inplace=True)

        df = upward_prices.join(downward_prices, how='inner', rsuffix='_down', sort=True)

        if df.size == 0:
            raise Exception("This file doesn't look like e.sios balancing prices")

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


@app.route('/api/markets/summary/<mkt_id>')
def get_summary(mkt_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        market = db.session.query(Market).filter_by(id=mkt_id).first()
        data = market.get_summary()

        js = jsonify({'data': data})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/markets/prices/<mkt_id>/<value_name>')
def get_values(mkt_id, value_name):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        values = db.session.query(Prices.time, getattr(Prices, value_name)) \
            .filter_by(market_id=mkt_id) \
            .order_by(Prices.time) \
            .all()

        values = [[calendar.timegm(x[0].utctimetuple()) * 1000, x[1]] for x in values]

        js = jsonify({'data': values})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/markets/prices/calculate_missing/<mkt_id>', methods=['POST', ])
def calculate_missing(mkt_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        market = db.session.query(Market).filter_by(id=mkt_id).first()
        market.calculate_missing_values()
        db.session.commit()

        js = jsonify({'data': 'OK'})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/markets/prices/fit_model/<mkt_id>', methods=['POST', ])
def fit_model(mkt_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        market = db.session.query(Market).filter_by(id=mkt_id).first()
        market.fit_price_model()
        db.session.commit()

        js = jsonify({'data': 'OK'})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js
