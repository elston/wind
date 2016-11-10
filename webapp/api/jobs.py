import logging
import pickle

from flask import jsonify
from flask_login import current_user
from rq.compat import as_text, decode_redis_hash
from rq.exceptions import UnpickleError
from rq.utils import utcparse
from webapp import app, sch
from webapp.tasks import redis_conn

logger = logging.getLogger(__name__)


@app.route('/api/scheduler/jobs')
def list_jobs():
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        jobs = sch.scheduler.get_jobs()
        table_data = [{'name': x.name,
                       'id': x.id,
                       'next_run_time': x.next_run_time.strftime('%d %b %Y %I:%M%p %Z%z')
                       } for x in jobs]

        js = jsonify({'data': table_data})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


def get_all_jobs(queue=None):
    def to_date(date_str):
        if date_str is None:
            return
        else:
            return utcparse(as_text(date_str))

    def unpickle(pickled_string):
        try:
            obj = pickle.loads(pickled_string)
        except Exception as e:
            raise UnpickleError('Could not unpickle.', pickled_string, e)
        return obj

    job_ids = redis_conn.keys('rq:job:*')
    jobs = {}

    for job_id in job_ids:
        obj = decode_redis_hash(redis_conn.hgetall(job_id))
        if len(obj) == 0:
            pass
        if queue is not None:
            if queue != as_text(obj.get('origin')):
                pass
        jobs[job_id] = {
            'job_id': job_id.replace('rq:job:', ''),
            'created_at': obj.get('created_at'),
            'enqueued_at': to_date(as_text(obj.get('enqueued_at'))),
            'ended_at': to_date(as_text(obj.get('ended_at'))),
            # 'result': unpickle(obj.get('result')) if obj.get('result') else None,
            'exc_info': obj.get('exc_info'),
            'status': as_text(obj.get('status') if obj.get('status') else None),
            # 'meta': unpickle(obj.get('meta')) if obj.get('meta') else {}
        }

    return jobs


@app.route('/api/rq/jobs')
def list_rq_jobs():
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        table_data = get_all_jobs().values()
        js = jsonify({'data': table_data})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js
