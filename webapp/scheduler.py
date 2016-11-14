import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
import pytz
from webapp import db, app
from .models import Location
import webapp.tasks

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class Scheduler(object):
    def __init__(self):
        jobstores = {
            'default': SQLAlchemyJobStore(url=app.config['SCHEDULER_DATABASE_URI'])
        }
        executors = {
            'default': ThreadPoolExecutor(20),
            # 'processpool': ProcessPoolExecutor(5)
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3
        }
        self.scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)

    def update_weather_schedules(self):
        locations = db.session.query(Location)
        for location in locations:
            if location.tz_long is None:
                continue
            timezone = pytz.timezone(location.tz_long)
            if timezone is None:
                continue
            job_id = 'user_%s_forecast_update_%s_11am' % (location.user_id, location.l)
            if location.update_at_11am:
                job = self.scheduler.add_job(webapp.tasks.start_forecast_update, args=(location.id,), id=job_id,
                                             trigger='cron',
                                             hour=11, minute=0, replace_existing=True, timezone=timezone)
            else:
                try:
                    self.scheduler.remove_job(job_id)
                except:
                    pass
            job_id = 'user_%s_forecast_update_%s_11pm' % (location.user_id, location.l)
            if location.update_at_11pm:
                job = self.scheduler.add_job(webapp.tasks.start_forecast_update, args=(location.id,), id=job_id,
                                             trigger='cron',
                                             hour=23, minute=0, replace_existing=True, timezone=timezone)
            else:
                try:
                    self.scheduler.remove_job(job_id)
                except:
                    pass

    def start(self):
        self.scheduler.start()
