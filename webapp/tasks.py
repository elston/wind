import logging
import signal
import urllib

import psutil as psutil
import os
from rq import Queue, get_current_job, Connection, Worker
from redis import Redis
from rq.job import Job
from webapp import db
from webapp.models import Windpark, Location
from webapp.models.optimization_job import OptimizationJob
from webapp.optimizer import Optimizer

redis_conn = Redis()
q = Queue(connection=redis_conn)


class RqLogHandler(logging.Handler):
    def __init__(self, job):
        logging.Handler.__init__(self)
        self.job = job
        self.job.meta['log'] = []
        self.job.save()
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    def flush(self):
        pass

    def emit(self, record):
        try:
            print record.name
            if record.name != 'rq.worker':
                msg = self.format(record)
                self.job.refresh()
                self.job.meta['log'].append(msg)
                self.job.save()
                print self.job.status, msg
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


def start_windpark_optimization(windpark_id, job_parameters=OptimizationJob()):
    job_id = 'windpark_opt_%d' % windpark_id
    job = q.enqueue(windpark_optimizer_job, windpark_id, job_parameters, job_id=job_id, timeout=1200, result_ttl=-1)
    return job


def windpark_optimization_status(windpark_id):
    return q.fetch_job('windpark_opt_%d' % windpark_id)

def kill_job(job_id):
    with Connection():
        ws = Worker.all()
        for w in ws:
            if w.get_current_job_id() == job_id:
                host, pid = w.name.split('.')
                pid = int(pid)
                try:
                    w_process = psutil.Process(pid)
                    children = w_process.children()
                    if len(children) > 0:
                        os.kill(children[0].pid, signal.SIGKILL)
                except Exception, e:
                    logging.exception("Can't kill worker")
        job = Job.fetch(job_id)
        job.delete()


def cancel_job(job_id):
    with Connection():
        job = Job.fetch(job_id)
        job.delete()


def windpark_optimizer_job(windpark_id, job_parameters=OptimizationJob()):
    with Connection():
        job = get_current_job()
        print 'Current job: %s' % (job.id,)
        opt = Optimizer(windpark_id, log_handler=RqLogHandler(job))
        result = opt.optimize(job_parameters)

        windpark = db.session.query(Windpark).filter_by(id=windpark_id).first()
        windpark.optimization_results = result
        db.session.commit()

        return result.to_dict()


def start_forecast_update(location_id):
    job_id = urllib.urlencode(
        {'job': 'wu_download', 'location': location_id})  # , 'id': datetime.utcnow().isoformat()})
    job = q.enqueue(forecast_update_job, location_id, timeout=1200, result_ttl=-1, job_id=job_id)
    return job


def forecast_update_job(location_id):
    with Connection():
        job = get_current_job()
        print 'Current job: %s' % (job.id,)
        logging.getLogger().addHandler(RqLogHandler(job))
        # logging.info("Scheduled update for location %s", location.name)
        try:
            location = db.session.query(Location).filter_by(id=location_id).first()
            location.update_history()
        finally:
            db.session.remove()
        try:
            location = db.session.query(Location).filter_by(id=location_id).first()
            location.update_forecast()
        finally:
            db.session.remove()
