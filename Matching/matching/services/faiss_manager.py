import os
import threading

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

FAISS_DIR = "/app/data"
FAISS_INDEX_PATH = os.path.join(FAISS_DIR, "jobs.index")

os.makedirs(FAISS_DIR, exist_ok=True)


model = SentenceTransformer(MODEL_NAME)

dimension = model.get_sentence_embedding_dimension()

_index = None
_lock = threading.RLock()


def _create_index():
    base_index = faiss.IndexFlatIP(dimension)
    return faiss.IndexIDMap2(base_index)


def load_index():
    global _index

    with _lock:
        if os.path.exists(FAISS_INDEX_PATH):
            _index = faiss.read_index(FAISS_INDEX_PATH)
        else:
            _index = _create_index()

    return _index


def get_index():
    global _index

    if _index is None:
        load_index()

    return _index


def save_index():
    with _lock:
        faiss.write_index(_index, FAISS_INDEX_PATH)


def add_job(job_id: int, description: str):
    global _index

    if not description:
        return

    with _lock:
        vector = model.encode(
            description,
            normalize_embeddings=True,
        )

        vector = np.asarray(vector, dtype="float32").reshape(1, -1)

        # Remove old vector if it already exists.
        remove_job(job_id)

        ids = np.array([job_id], dtype=np.int64)

        _index.add_with_ids(vector, ids)

        faiss.write_index(_index, FAISS_INDEX_PATH)


def remove_job(job_id: int):
    global _index

    with _lock:
        if _index is None:
            load_index()

        ids = np.array([job_id], dtype=np.int64)

        _index.remove_ids(ids)

        faiss.write_index(_index, FAISS_INDEX_PATH)


def search(vector, top_k=50):
    index = get_index()

    if index.ntotal == 0:
        return [], []

    vector = np.asarray(vector, dtype="float32").reshape(1, -1)

    scores, ids = index.search(vector, top_k)

    return scores[0], ids[0]
