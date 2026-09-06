import numpy as np
import requests
from celery import shared_task
from decouple import config
from sentence_transformers import SentenceTransformer

from .models import JobMatch, IndexedJob
from matching.services.faiss_manager import add_job, remove_job, search

# Load embedding model once
model = SentenceTransformer("all-MiniLM-L6-v2")

JOB_SERVICE_URL = config("JOB_SERVICE_URL") + "/api/v1/internal/jobs"
APPLICATION_SERVICE_URL = config("APPLICATION_SERVICE_URL") + "/api/v1/internal/cvs/"
headers = {"X-Service-Token": config("INTERNAL_SERVICE_TOKEN")}


# @shared_task
# def match_all_cvs_to_new_job(job_id, job_description):

#     job_vec = model.encode(job_description)

#     # Fetch all CVs from application service
#     response = requests.get(APPLICATION_SERVICE_URL, headers=headers)
#     if response.status_code != 200:
#         raise Exception("Failed to fetch CVs from Application Service")
#     cvs = response.json()

#     results = []

#     for cv in cvs:
#         cv_text = cv["extracted_text"]

#         cv_vec = model.encode(cv_text)
#         score = cosine_similarity(job_vec, cv_vec)
#         results.append((cv["user_id"], score))

#     # Store top 5 matches
#     top_matches = sorted(results, key=lambda x: x[1], reverse=True)[:5]
#     for user_id, score in top_matches:
#         JobMatch.objects.create(user_id=user_id, job_id=job_id, score=score)


@shared_task
def match_new_cv_to_all_jobs(user_id, cv_text):

    if not cv_text:
        return

    cv_vec = model.encode(
        cv_text,
        normalize_embeddings=True,
    )

    cv_vec = np.asarray(
        cv_vec,
        dtype="float32",
    ).reshape(1, -1)

    scores, faiss_ids = search(
        cv_vec,
        top_k=50,
    )

    candidates = []

    for score, faiss_id in zip(scores, faiss_ids):

        if faiss_id == -1:
            continue

        if score < 0.43:
            continue

        candidates.append((int(faiss_id), float(score)))

    # Keep best 5
    candidates = candidates[:5]

    for faiss_id, score in candidates:

        matching_job = IndexedJob.objects.filter(
            faiss_index_id=faiss_id,
            is_active=True,
        ).first()

        if not matching_job:
            continue

        JobMatch.objects.update_or_create(
            user_id=user_id,
            job_id=matching_job.job_id,
            defaults={
                "score": score,
            },
        )


@shared_task(
    autoretry_for=(requests.RequestException,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def sync_job_to_faiss(job_id):
    headers = {"X-Service-Token": config("INTERNAL_SERVICE_TOKEN")}

    url = f"{JOB_SERVICE_URL}/{job_id}/"

    response = requests.get(
        url,
        headers=headers,
        timeout=5,
    )

    if response.status_code == 404:
        IndexedJob.objects.filter(job_id=job_id).delete()
        return

    response.raise_for_status()

    job = response.json()

    description = job.get("description", "")
    status_value = job.get("status", True)

    matching_job, _ = IndexedJob.objects.update_or_create(
        job_id=job_id,
        defaults={
            "description": description,
            "is_active": status_value,
        },
    )

    # Inactive jobs should not be in FAISS.
    if not status_value:
        if matching_job.faiss_index_id is not None:
            remove_job(matching_job.faiss_index_id)

            matching_job.faiss_index_id = None
            matching_job.save(update_fields=["faiss_index_id", "updated_at"])

        return

    # Create a FAISS ID if this job doesn't have one.
    if matching_job.faiss_index_id is None:
        # We need a unique integer ID for FAISS.
        max_id = (
            IndexedJob.objects.exclude(faiss_index_id__isnull=True)
            .order_by("-faiss_index_id")
            .values_list("faiss_index_id", flat=True)
            .first()
        )

        faiss_id = (max_id or 0) + 1

        matching_job.faiss_index_id = faiss_id
        matching_job.save(update_fields=["faiss_index_id", "updated_at"])
    else:
        faiss_id = matching_job.faiss_index_id

    add_job(
        job_id=faiss_id,
        description=description,
    )


@shared_task
def remove_job_from_faiss(job_id):

    try:
        matching_job = IndexedJob.objects.get(job_id=job_id)

    except IndexedJob.DoesNotExist:
        return

    if matching_job.faiss_index_id is not None:
        remove_job(matching_job.faiss_index_id)

    matching_job.delete()
