# jobs/tasks.py

import requests

from celery import shared_task
from decouple import config

MATCHING_SERVICE_URL = config("MATCHING_SERVICE_URL") + "/api/v1/internal/events/job/"


@shared_task(
    autoretry_for=(requests.RequestException,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def notify_matching_service(event, job_id, data=None):

    url = MATCHING_SERVICE_URL

    headers = {
        "X-Service-Token": config("INTERNAL_SERVICE_TOKEN"),
    }

    payload = {
        "event": event,
        "job_id": str(job_id),
        "data": data or {},
    }

    response = requests.post(
        url,
        json=payload,
        headers=headers,
        timeout=5,
    )

    response.raise_for_status()
