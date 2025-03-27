# mcsu_sop/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mcsu_sop.settings')

app = Celery('mcsu_sop')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Windows-specific settings
app.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    worker_pool_restarts=True,
    task_track_started=True,
)

app.conf.beat_schedule = {
    'send-daily-reminder-emails': {
        'task': 'initiatives.tasks.send_reminder_emails',
        'schedule': crontab(minute='*/1'), 
    },
}