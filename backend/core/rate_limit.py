import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass

from fastapi import Request


@dataclass
class RateLimitResult:
    allowed: bool
    retry_after_seconds: int = 0
    client_ip: str = "unknown"


class InMemoryRateLimiter:
    """
    MVP-only in-memory limiter.

    This protects Gemini quota for a single-process deployment but is not suitable
    for multi-instance scaling. Replace with Redis or another shared store later.
    """

    def __init__(self, *, limit: int, window_seconds: int) -> None:
        self.limit = limit
        self.window_seconds = window_seconds
        self._lock = threading.Lock()
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    def check(self, request: Request, scope: str) -> RateLimitResult:
        now = time.time()
        client_ip = self._get_client_ip(request)
        key = f"{scope}:{client_ip}"

        with self._lock:
            bucket = self._requests[key]
            while bucket and now - bucket[0] >= self.window_seconds:
                bucket.popleft()

            if len(bucket) >= self.limit:
                retry_after = max(1, int(self.window_seconds - (now - bucket[0])))
                return RateLimitResult(
                    allowed=False,
                    retry_after_seconds=retry_after,
                    client_ip=client_ip,
                )

            bucket.append(now)

        return RateLimitResult(allowed=True, client_ip=client_ip)

    @staticmethod
    def _get_client_ip(request: Request) -> str:
        forwarded_for = request.headers.get("x-forwarded-for", "").strip()
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip", "").strip()
        if real_ip:
            return real_ip

        if request.client and request.client.host:
            return request.client.host

        return "unknown"
