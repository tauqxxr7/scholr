import hashlib
import time
from typing import Optional


class ResponseCache:
    def __init__(self, ttl_seconds: int = 3600, max_entries: int = 500):
        self._cache: dict[str, tuple[str, float]] = {}
        self._ttl = ttl_seconds
        self._max = max_entries

    def _key(self, module: str, query: str, mode: str) -> str:
        raw = f"{module}:{query.strip().lower()}:{mode}"
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, module: str, query: str, mode: str) -> Optional[str]:
        key = self._key(module, query, mode)
        entry = self._cache.get(key)
        if entry is None:
            return None
        content, ts = entry
        if time.time() - ts >= self._ttl:
            del self._cache[key]
            return None
        return content

    def set(self, module: str, query: str, mode: str, content: str) -> None:
        if len(self._cache) >= self._max:
            # Evict oldest entry.
            oldest = min(self._cache, key=lambda k: self._cache[k][1])
            del self._cache[oldest]
        key = self._key(module, query, mode)
        self._cache[key] = (content, time.time())

    def stats(self) -> dict:
        now = time.time()
        valid = sum(1 for _, ts in self._cache.values() if now - ts <= self._ttl)
        return {"total_entries": len(self._cache), "valid_entries": valid, "ttl_seconds": self._ttl}


# Singleton shared across all requests in the current worker.
response_cache = ResponseCache(ttl_seconds=3600, max_entries=500)
