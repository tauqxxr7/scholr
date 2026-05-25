import hashlib
import math
import os
import re

_model = None
_MODEL_DISABLED = object()
_DIMENSIONS = 64


def _get_model():
    global _model
    if os.getenv("ENABLE_SENTENCE_TRANSFORMERS", "").lower() not in {"1", "true", "yes"}:
        return None
    if _model is _MODEL_DISABLED:
        return None
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer

            _model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            _model = _MODEL_DISABLED
            return None
    return _model


def _fallback_embedding(text: str) -> list[float]:
    vector = [0.0] * _DIMENSIONS
    tokens = re.findall(r"[a-z0-9]+", text.lower()[:512])
    for token in tokens:
        digest = hashlib.sha256(token.encode()).digest()
        index = int.from_bytes(digest[:2], "big") % _DIMENSIONS
        sign = 1.0 if digest[2] % 2 == 0 else -1.0
        vector[index] += sign
    norm = math.sqrt(sum(value * value for value in vector))
    return [value / norm for value in vector] if norm else vector


def embed_text(text: str) -> list[float]:
    model = _get_model()
    if model is not None:
        try:
            return model.encode(text[:512], normalize_embeddings=True).tolist()
        except Exception:
            pass
    return _fallback_embedding(text)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(left * right for left, right in zip(a, b))
    left_norm = math.sqrt(sum(value * value for value in a))
    right_norm = math.sqrt(sum(value * value for value in b))
    denom = left_norm * right_norm
    return dot / denom if denom > 0 else 0.0
