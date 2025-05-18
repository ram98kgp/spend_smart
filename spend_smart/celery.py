# project/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spend_smart.settings')

# Create the Celery app
app = Celery('spend_smart')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure the Celery beat schedule
app.conf.beat_schedule = {
    'check-budget-thresholds': {
        'task': 'tracker.tasks.check_budget_thresholds',
        # Run every hour
        'schedule': crontab(minute='*'),
        # Alternatively, run daily at midnight
        # 'schedule': crontab(minute=0, hour=0),
        # Or run every 30 minutes
        # 'schedule': crontab(minute='*/30'),
    },
}