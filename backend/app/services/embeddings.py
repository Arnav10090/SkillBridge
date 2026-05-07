from functools import lru_cache
import hashlib
import re
import numpy as np
from app.core.config import settings

@lru_cache(maxsize=1)
def get_embedding_service():
    return EmbeddingService()

class EmbeddingService:
    def __init__(self):
        self.dimensions = settings.EMBEDDING_DIMENSIONS

    def embed(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, self.dimensions), dtype=np.float32)

        vecs = np.vstack([self._embed_one(text) for text in texts]).astype(np.float32)
        norms = np.linalg.norm(vecs, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return vecs / norms

    def similarity(self, a: str, b: str) -> float:
        vecs = self.embed([a, b])
        return float(np.dot(vecs[0], vecs[1]))

    def _embed_one(self, text: str) -> np.ndarray:
        vec = np.zeros(self.dimensions, dtype=np.float32)
        normalized = re.sub(r"[^a-z0-9+#.]+", " ", text.lower()).strip()
        if not normalized:
            return vec

        tokens = normalized.split()
        features = tokens + self._char_ngrams(normalized.replace(" ", "_"))

        for feature in features:
            digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
            hashed = int.from_bytes(digest, "big")
            index = hashed % self.dimensions
            sign = 1.0 if hashed & 1 else -1.0
            vec[index] += sign

        return vec

    @staticmethod
    def _char_ngrams(text: str) -> list[str]:
        padded = f" {text} "
        return [
            padded[i:i + size]
            for size in (3, 4)
            for i in range(max(len(padded) - size + 1, 0))
        ]
