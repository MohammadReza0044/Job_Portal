import os
import threading

import faiss
import numpy as np

from matching.services.faiss_manager import model, dimension

FAISS_DIR = "/app/data"
FAISS_INDEX_PATH = os.path.join(FAISS_DIR, "cvs.index")

os.makedirs(FAISS_DIR, exist_ok=True)


_cv_index = None
_cv_lock = threading.RLock()


def _create_index():
    base_index = faiss.IndexFlatIP(dimension)
    return faiss.IndexIDMap2(base_index)


def load_cv_index():
    global _cv_index

    with _cv_lock:
        if os.path.exists(FAISS_INDEX_PATH):
            _cv_index = faiss.read_index(FAISS_INDEX_PATH)
        else:
            _cv_index = _create_index()

    return _cv_index


def get_cv_index():
    global _cv_index

    if _cv_index is None:
        load_cv_index()

    return _cv_index


def save_cv_index():
    with _cv_lock:
        index = get_cv_index()
        faiss.write_index(index, FAISS_INDEX_PATH)


def add_cv(cv_id: int, cv_text: str):
    global _cv_index

    if not cv_text:
        return

    with _cv_lock:
        index = get_cv_index()

        # Encode the CV using the same model as job embeddings.
        vector = model.encode(
            cv_text,
            normalize_embeddings=True,
        )

        vector = np.asarray(
            vector,
            dtype="float32",
        ).reshape(1, -1)

        # Replace the old vector if this CV is already indexed.
        ids = np.array([cv_id], dtype=np.int64)
        index.remove_ids(ids)

        index.add_with_ids(vector, ids)

        faiss.write_index(index, FAISS_INDEX_PATH)


def remove_cv(cv_id: int):
    with _cv_lock:
        index = get_cv_index()

        ids = np.array([cv_id], dtype=np.int64)

        index.remove_ids(ids)

        faiss.write_index(index, FAISS_INDEX_PATH)


def search_cvs(vector, top_k=50):
    index = get_cv_index()

    if index.ntotal == 0:
        return [], []

    vector = np.asarray(
        vector,
        dtype="float32",
    ).reshape(1, -1)

    scores, ids = index.search(vector, top_k)

    return scores[0], ids[0]
