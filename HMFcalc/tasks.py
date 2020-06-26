"""
Created on Jun 12, 2013

@author: Steven
"""

from time import time

from celery.decorators import periodic_task
from celery.task.schedules import crontab
from django.conf import settings


# this will run every minute,
# see http://celeryproject.org/docs/reference/celery.task.schedules.html#celery.task.schedules.crontab
@periodic_task(run_every=crontab(hour="*", minute="*", day_of_week="*"))
def writefile():
    print("Writing to file...")
    with open(settings.ROOT_DIR + "/heartbeat", "a") as f:
        f.write(str(time()))
