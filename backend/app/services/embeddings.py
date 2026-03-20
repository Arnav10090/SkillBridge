from sentence_transformers import SentenceTransformer
from functools import lru_cache
import numpy as np
from app.core.config import settings

@lru_cache(maxsize=1)
def get_embedding_service():
    return EmbeddingService()

class EmbeddingService:
    def __init__(self):
        print(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        print("Embedding model ready.")

    def embed(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.array([])
        vecs = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return np.array(vecs, dtype=np.float32)

    def similarity(self, a: str, b: str) -> float:
        vecs = self.embed([a, b])
        return float(np.dot(vecs[0], vecs[1]))