from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.broker_url = "redis://localhost:6379/0"

app.autodiscover_tasks()

# periodic task schedule
app.conf.beat_schedule = {
    "clean-expired-job-matches-every-3-minutes": {
        "task": "matching.tasks.clean_expired_matches",
        "schedule": crontab(minute="*/1"),
    },
}
