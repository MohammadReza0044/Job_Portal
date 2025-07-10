import os

import numpy as np
import requests
from celery import shared_task
from decouple import config
from django.conf import settings
from sentence_transformers import SentenceTransformer

from .models import JobMatch

# Load embedding model once
model = SentenceTransformer("all-MiniLM-L6-v2")

JOB_SERVICE_URL = "http://localhost:8000/api/internal/jobs/"
APPLICATION_SERVICE_URL = "http://localhost:8003/api/application/internal/cvs/"
headers = {"X-Service-Token": config("INTERNAL_SERVICE_TOKEN")}


@shared_task
def match_all_cvs_to_new_job(job_id, job_description):

    job_vec = model.encode(job_description)

    # Fetch all CVs from application service
    response = requests.get(APPLICATION_SERVICE_URL, headers=headers)
    if response.status_code != 200:
        raise Exception("Failed to fetch CVs from Application Service")
    cvs = response.json()

    results = []

    for cv in cvs:
        cv_text = cv["extracted_text"]

        cv_vec = model.encode(cv_text)
        score = cosine_similarity(job_vec, cv_vec)
        results.append((cv["user_id"], score))

    # Store top 5 matches
    top_matches = sorted(results, key=lambda x: x[1], reverse=True)[:5]
    for user_id, score in top_matches:
        JobMatch.objects.create(user_id=user_id, job_id=job_id, score=score)


@shared_task
def match_new_cv_to_all_jobs(user_id, cv_text):

    cv_vec = model.encode(cv_text)

    # Fetch all jobs from job service
    response = requests.get(JOB_SERVICE_URL, headers=headers)
    if response.status_code != 200:
        raise Exception("Failed to fetch jobs from Job Service")
    jobs = response.json()

    results = []
    for job in jobs:
        job_vec = model.encode(job["description"])
        score = cosine_similarity(cv_vec, job_vec)
        results.append((job["id"], score))

    # Store top 5 matches
    top_matches = sorted(results, key=lambda x: x[1], reverse=True)[:5]
    for job_id, score in top_matches:
        JobMatch.objects.create(user_id=user_id, job_id=job_id, score=score)


def cosine_similarity(vec1, vec2):
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
