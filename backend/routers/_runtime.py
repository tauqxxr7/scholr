import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from core.logging_utils import log_event
from core.rate_limit import InMemoryRateLimiter
from db import crud
from db.database import SearchHistory

logger = logging.getLogger(__name__)

ai_rate_limiter = InMemoryRateLimiter(limit=10, window_seconds=60)


def enforce_rate_limit(request: Request, module: str) -> JSONResponse | None:
    result = ai_rate_limiter.check(request, module)
    if result.allowed:
        return None

    request_id = getattr(request.state, "request_id", None)
    log_event(
        logger,
        "rate_limited",
        module=module,
        request_id=request_id,
        client_ip=result.client_ip,
        retry_after_seconds=result.retry_after_seconds,
    )

    return JSONResponse(
        status_code=429,
        headers={"Retry-After": str(result.retry_after_seconds)},
        content={
            "detail": "Scholr is handling too many requests from this connection right now. Please wait a moment and try again."
        },
    )


def find_cached_response(
    db: Session,
    *,
    module: str,
    query: str,
    request_id: str | None,
) -> SearchHistory | None:
    cached = crud.get_cached_search(db, module=module, query=query)

    log_event(
        logger,
        "cache_hit" if cached else "cache_miss",
        module=module,
        request_id=request_id,
    )
    return cached
