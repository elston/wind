import logging

from flask import jsonify
from flask_security import login_required
from webapp import app

logger = logging.getLogger(__name__)


@app.route('/api/location')
@login_required
def get_location():
    try:
        js = jsonify({'data': 'OK'})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js
