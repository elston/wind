import logging
import pickle
import urlparse

from flask import jsonify
from flask_login import current_user
from rq.compat import as_text, decode_redis_hash
from rq.exceptions import UnpickleError
from rq.utils import utcparse
from webapp import app
import webapp
from webapp.models import Location, Windpark
import webapp.tasks

logger = logging.getLogger(__name__)


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

    job_ids = webapp.tasks.redis_conn.keys('rq:job:*')
    jobs = {}

    for job_id in job_ids:
        obj = decode_redis_hash(webapp.tasks.redis_conn.hgetall(job_id))
        if len(obj) == 0:
            pass
        if queue is not None:
            if queue != as_text(obj.get('origin')):
                pass
        jobs[job_id] = {
            'job_id': job_id.replace('rq:job:', ''),
            'created_at': obj.get('created_at'),
            # 'enqueued_at': to_date(as_text(obj.get('enqueued_at'))),
            'enqueued_at': obj.get('enqueued_at'),
            'ended_at': obj.get('ended_at'),
            # 'result': unpickle(obj.get('result')) if obj.get('result') else None,
            'exc_info': obj.get('exc_info'),
            'status': as_text(obj.get('status') if obj.get('status') else None),
            'meta': unpickle(obj.get('meta')) if obj.get('meta') else {}
        }

    return jobs


@app.route('/api/status')
def list_jobs():
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        jobs = webapp.sch.scheduler.get_jobs()
        scheduler_data = [{'name': x.name,
                           'id': x.id,
                           'next_run_time': x.next_run_time.strftime('%d %b %Y %I:%M%p %Z%z')
                           } for x in jobs]

        rqjobs_data = []
        for item in get_all_jobs().itervalues():
            id_data = {k: v[0] for k, v in urlparse.parse_qs(item['job_id']).iteritems()}
            try:
                if id_data.get('job') == 'wu_download':
                    location_id = id_data.get('location')
                    location = webapp.db.session.query(Location).filter_by(id=location_id).first()
                    name = 'WU download for location %s' % location.name
                elif id_data.get('job') == 'optimize':
                    windpark_id = id_data.get('windpark')
                    windpark = webapp.db.session.query(Windpark).filter_by(id=windpark_id).first()
                    name = 'Optimization for wind park %s' % windpark.name
                else:
                    name = item['job_id']
            except:
                name = item['job_id']
            item.update(id_data)
            item['name'] = name
            rqjobs_data.append(item)

        interlocks = {'windparks': set(), 'locations': set(), 'markets': set()}

        for rqjob in rqjobs_data:
            if 'windpark' in rqjob and rqjob.get('status') not in ('finished', 'failed'):
                windpark_id = int(rqjob['windpark'])
                interlocks['windparks'].add(windpark_id)
                windpark = webapp.db.session.query(Windpark).filter_by(id=windpark_id).first()
                interlocks['locations'].add(windpark.location_id)
                interlocks['markets'].add(windpark.market_id)
            elif 'location' in rqjob and rqjob.get('status') not in ('finished', 'failed'):
                location_id = int(rqjob['location'])
                interlocks['locations'].add(location_id)
                windparks = webapp.db.session.query(Windpark).filter_by(location_id=location_id).all()
                for windpark in windparks:
                    interlocks['windparks'].add(windpark.id)
            elif 'market' in rqjob and rqjob.get('status') not in ('finished', 'failed'):
                market_id = int(rqjob['market'])
                interlocks['markets'].add(market_id)
                windparks = webapp.db.session.query(Windpark).filter_by(market_id=market_id).all()
                for windpark in windparks:
                    interlocks['windparks'].add(windpark.id)

        interlocks = {k: list(v) for k, v in interlocks.iteritems()}

        js = jsonify({'data': {'scheduler': scheduler_data, 'rqjobs': rqjobs_data, 'interlocks': interlocks}})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/rqjobs/<job_id>/cancel', methods=['POST', ])
def cancel_job(job_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        webapp.tasks.cancel_job(job_id)
        js = jsonify({'data': 'OK'})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js


@app.route('/api/rqjobs/<job_id>/kill', methods=['POST', ])
def kill_job(job_id):
    if not current_user.is_authenticated:
        return jsonify({'error': 'User unauthorized'})
    try:
        webapp.tasks.kill_job(job_id)
        js = jsonify({'data': 'OK'})
        return js
    except Exception, e:
        logger.exception(e)
        js = jsonify({'error': repr(e)})
        return js
