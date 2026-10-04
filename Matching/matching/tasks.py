import numpy as np
import requests
from celery import shared_task
from decouple import config

from .models import *

from .services.embedding_model import model
from .services.mongodb_vector_store import (
    upsert_cv_vector,
    search_cvs,
    search_jobs,
    delete_cv_vector,
    delete_job_vector,
    upsert_job_vector,
)

JOB_SERVICE_URL = config("JOB_SERVICE_URL") + "/api/v1/internal/jobs"
APPLICATION_SERVICE_URL = config("APPLICATION_SERVICE_URL") + "/api/v1/internal/cvs/"
headers = {"X-Service-Token": config("INTERNAL_SERVICE_TOKEN")}


@shared_task
def index_cv(user_id, cv_text):
    if not cv_text:
        return

    embedding = model.encode(
        cv_text,
        normalize_embeddings=True,
    )

    upsert_cv_vector(
        user_id=user_id,
        embedding=embedding,
    )

    print(f"CV vector stored in MongoDB. " f"user_id={user_id}")


@shared_task
def remove_cv_vector(user_id):
    JobMatch.objects.filter(user_id=user_id).delete()

    delete_cv_vector(user_id)

    print(f"CV vector removed from MongoDB. " f"user_id={user_id}")


@shared_task
def match_new_job_to_all_cvs(job_id, job_description):

    if not job_description:
        return

    job_vec = model.encode(
        job_description,
        normalize_embeddings=True,
    )

    results = search_cvs(
        query_vector=job_vec,
        top_k=50,
        num_candidates=1000,
    )

    for result in results:
        score = float(result["score"])

        if score < 0.43:
            continue

        user_id = result["user_id"]

        JobMatch.objects.update_or_create(
            user_id=user_id,
            job_id=job_id,
            defaults={
                "score": score,
            },
        )


@shared_task
def match_new_cv_to_all_jobs(user_id, cv_text):
    if not cv_text:
        return

    cv_vec = model.encode(
        cv_text,
        normalize_embeddings=True,
    )

    results = search_jobs(
        query_vector=cv_vec,
        top_k=50,
        num_candidates=1000,
    )

    for result in results:
        score = float(result["score"])

        if score < 0.43:
            continue

        job_id = result["job_id"]

        JobMatch.objects.update_or_create(
            user_id=user_id,
            job_id=job_id,
            defaults={
                "score": score,
            },
        )


@shared_task
def sync_job_vector(job_id):
    url = f"{JOB_SERVICE_URL}/{job_id}/"

    headers = {"X-Service-Token": config("INTERNAL_SERVICE_TOKEN")}

    response = requests.get(
        url,
        headers=headers,
        timeout=5,
    )

    if response.status_code == 404:
        delete_job_vector(job_id)
        return

    response.raise_for_status()

    job = response.json()

    description = job.get("description")

    if not description:
        return

    embedding = model.encode(
        description,
        normalize_embeddings=True,
    )

    upsert_job_vector(
        job_id=job_id,
        embedding=embedding,
        is_active=job.get("status", True),
    )


@shared_task
def remove_job_vector(job_id):

    JobMatch.objects.filter(job_id=job_id).delete()

    delete_job_vector(job_id)

    print(f"Job vector removed from MongoDB. " f"job_id={job_id}")
