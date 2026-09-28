import numpy as np
import requests
from celery import shared_task
from decouple import config
from sentence_transformers import SentenceTransformer

from .models import *
from matching.services.faiss_manager import add_job, remove_job, search
from matching.services.cv_faiss_manager import (
    add_cv,
    remove_cv,
    search_cvs,
)

# Load embedding model once
model = SentenceTransformer("all-MiniLM-L6-v2")

JOB_SERVICE_URL = config("JOB_SERVICE_URL") + "/api/v1/internal/jobs"
APPLICATION_SERVICE_URL = config("APPLICATION_SERVICE_URL") + "/api/v1/internal/cvs/"
headers = {"X-Service-Token": config("INTERNAL_SERVICE_TOKEN")}


@shared_task
def index_cv(user_id, cv_text):
    if not cv_text:
        return

    print(f"[index_cv] Starting CV indexing for user: {user_id}")

    indexed_cv, created = IndexedCV.objects.get_or_create(
        user_id=user_id,
        defaults={
            "extracted_text": cv_text,
        },
    )

    print(
        f"[index_cv] IndexedCV {'created' if created else 'found'}: " f"{indexed_cv.id}"
    )

    # Keep the stored text up to date
    indexed_cv.extracted_text = cv_text

    # Assign a unique FAISS ID if this CV doesn't have one
    if indexed_cv.faiss_index_id is None:
        max_id = (
            IndexedCV.objects.exclude(faiss_index_id__isnull=True)
            .order_by("-faiss_index_id")
            .values_list("faiss_index_id", flat=True)
            .first()
        )

        indexed_cv.faiss_index_id = (max_id or 0) + 1

    indexed_cv.save(
        update_fields=[
            "extracted_text",
            "faiss_index_id",
            "updated_at",
        ]
    )

    print(
        f"[index_cv] IndexedCV saved. "
        f"user_id={user_id}, "
        f"faiss_index_id={indexed_cv.faiss_index_id}"
    )

    # Add/update the vector in FAISS
    add_cv(
        cv_id=indexed_cv.faiss_index_id,
        cv_text=cv_text,
    )

    print(
        f"[index_cv] CV successfully added to FAISS. "
        f"faiss_index_id={indexed_cv.faiss_index_id}"
    )


@shared_task
def remove_cv_from_faiss(user_id):
    indexed_cv = IndexedCV.objects.filter(user_id=user_id).first()

    # Delete any existing matches for this user
    JobMatch.objects.filter(user_id=user_id).delete()

    if not indexed_cv:
        return

    # Remove CV vector from FAISS
    if indexed_cv.faiss_index_id is not None:
        remove_cv(indexed_cv.faiss_index_id)

    # Remove the IndexedCV database record
    indexed_cv.delete()


@shared_task
def match_new_job_to_all_cvs(job_id, job_description):

    if not job_description:
        return

    # Encode only the new job
    job_vec = model.encode(
        job_description,
        normalize_embeddings=True,
    )

    job_vec = np.asarray(
        job_vec,
        dtype="float32",
    ).reshape(1, -1)

    # Search the precomputed CV vectors
    scores, faiss_ids = search_cvs(
        job_vec,
        top_k=50,
    )

    candidates = []

    for score, faiss_id in zip(scores, faiss_ids):
        if faiss_id == -1:
            continue

        if score < 0.43:
            continue

        candidates.append((int(faiss_id), float(score)))

    # Keep the top 5
    candidates = candidates[:5]

    # Resolve FAISS IDs to user IDs in one DB query
    indexed_cvs = IndexedCV.objects.filter(
        faiss_index_id__in=[faiss_id for faiss_id, _ in candidates]
    )

    user_by_faiss_id = {cv.faiss_index_id: cv.user_id for cv in indexed_cvs}

    for faiss_id, score in candidates:
        user_id = user_by_faiss_id.get(faiss_id)

        if user_id is None:
            continue

        JobMatch.objects.update_or_create(
            user_id=user_id,
            job_id=job_id,
            defaults={"score": score},
        )


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
