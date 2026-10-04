import os

import numpy as np
from pymongo import MongoClient
from pymongo.operations import SearchIndexModel

MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb://mongodb:27017",
)

MONGODB_DB_NAME = os.getenv(
    "MONGODB_DB_NAME",
    "matching_db",
)

JOB_COLLECTION_NAME = os.getenv(
    "MONGODB_JOB_COLLECTION",
    "job_vectors",
)

CV_COLLECTION_NAME = os.getenv(
    "MONGODB_CV_COLLECTION",
    "cv_vectors",
)

VECTOR_DIMENSION = 384

JOB_VECTOR_INDEX = "job_vector_index"
CV_VECTOR_INDEX = "cv_vector_index"


client = MongoClient(MONGODB_URI)

db = client[MONGODB_DB_NAME]

job_collection = db[JOB_COLLECTION_NAME]
cv_collection = db[CV_COLLECTION_NAME]


def check_connection():
    client.admin.command("ping")
    print("MongoDB connection successful")


def create_vector_indexes():
    """
    Creates the MongoDB Vector Search indexes.

    Safe to call multiple times.
    """

    job_definition = {
        "fields": [
            {
                "type": "vector",
                "numDimensions": VECTOR_DIMENSION,
                "path": "embedding",
                "similarity": "cosine",
            },
            {
                "type": "filter",
                "path": "is_active",
            },
        ]
    }

    cv_definition = {
        "fields": [
            {
                "type": "vector",
                "numDimensions": VECTOR_DIMENSION,
                "path": "embedding",
                "similarity": "cosine",
            }
        ]
    }

    _create_index_if_missing(
        job_collection,
        JOB_VECTOR_INDEX,
        job_definition,
    )

    _create_index_if_missing(
        cv_collection,
        CV_VECTOR_INDEX,
        cv_definition,
    )


def _create_index_if_missing(collection, index_name, definition):
    # MongoDB doesn't create the collection until the first document
    # is inserted, so explicitly create it before creating the
    # Vector Search index.
    if collection.name not in collection.database.list_collection_names():
        collection.database.create_collection(collection.name)

    existing_indexes = list(collection.list_search_indexes())

    for index in existing_indexes:
        if index.get("name") == index_name:
            print(f"Vector Search index already exists: {index_name}")
            return

    model = SearchIndexModel(
        definition=definition,
        name=index_name,
        type="vectorSearch",
    )

    collection.create_search_index(model=model)

    print(f"Created MongoDB Vector Search index " f"{index_name} on {collection.name}")


def _normalise_vector(vector):
    vector = np.asarray(
        vector,
        dtype="float32",
    ).reshape(-1)

    return vector.tolist()


# ============================================================
# JOB VECTORS
# ============================================================


def upsert_job_vector(
    job_id,
    embedding,
    is_active=True,
):
    """
    Create or update a job vector.
    """

    job_collection.update_one(
        {"job_id": str(job_id)},
        {
            "$set": {
                "job_id": str(job_id),
                "embedding": _normalise_vector(embedding),
                "is_active": bool(is_active),
            }
        },
        upsert=True,
    )


def delete_job_vector(job_id):
    """
    Completely remove a job vector.
    """

    job_collection.delete_one({"job_id": str(job_id)})


def update_job_status(job_id, is_active):
    """
    Activate/deactivate a job without deleting its vector.
    """

    job_collection.update_one(
        {"job_id": str(job_id)},
        {
            "$set": {
                "is_active": bool(is_active),
            }
        },
    )


def search_jobs(
    query_vector,
    top_k=50,
    num_candidates=1000,
):
    """
    Search active jobs using MongoDB Vector Search.
    """

    query_vector = _normalise_vector(query_vector)

    pipeline = [
        {
            "$vectorSearch": {
                "index": JOB_VECTOR_INDEX,
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": max(
                    num_candidates,
                    top_k,
                ),
                "limit": top_k,
                "filter": {
                    "is_active": True,
                },
            }
        },
        {
            "$project": {
                "_id": 0,
                "job_id": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]

    return list(job_collection.aggregate(pipeline))


# ============================================================
# CV VECTORS
# ============================================================


def upsert_cv_vector(
    user_id,
    embedding,
):
    """
    Create or update a CV vector.
    """

    cv_collection.update_one(
        {"user_id": str(user_id)},
        {
            "$set": {
                "user_id": str(user_id),
                "embedding": _normalise_vector(embedding),
            }
        },
        upsert=True,
    )


def delete_cv_vector(user_id):
    """
    Completely remove a CV vector.
    """

    cv_collection.delete_one({"user_id": str(user_id)})


def search_cvs(
    query_vector,
    top_k=50,
    num_candidates=1000,
):
    """
    Search CVs using MongoDB Vector Search.
    """

    query_vector = _normalise_vector(query_vector)

    pipeline = [
        {
            "$vectorSearch": {
                "index": CV_VECTOR_INDEX,
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": max(
                    num_candidates,
                    top_k,
                ),
                "limit": top_k,
            }
        },
        {
            "$project": {
                "_id": 0,
                "user_id": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]

    return list(cv_collection.aggregate(pipeline))
