import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
dimension = 384
index = faiss.IndexFlatL2(dimension)


def embed_text(text):
    return model.encode([text])[0]


def add_to_index(vector):
    index.add(np.array([vector]).astype("float32"))


def search_similar(vector, top_k=5):
    distances, indices = index.search(np.array([vector]).astype("float32"), top_k)
    return distances[0], indices[0]
