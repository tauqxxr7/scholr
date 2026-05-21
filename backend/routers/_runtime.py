import logging
from dataclasses import dataclass
from datetime import datetime

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from agents._generation import get_provider_status, request_provider_recovery
from core.auth import AuthContext
from core.logging_utils import log_event
from core.rate_limit import InMemoryRateLimiter
from db import crud
from db.database import SearchHistory
from routers._streaming import get_stream_observability

logger = logging.getLogger(__name__)

ai_rate_limiter = InMemoryRateLimiter(limit=10, window_seconds=60)
document_upload_rate_limiter = InMemoryRateLimiter(limit=6, window_seconds=60)
document_answer_rate_limiter = InMemoryRateLimiter(limit=12, window_seconds=60)
FREE_TIER_LIMITS = {
    "research": 40,
    "notes": 40,
    "doubt": 40,
    "documents_upload": 8,
    "documents_answer": 30,
}


@dataclass
class CachedResponseMatch:
    response: SearchHistory
    mode: str


def _daily_period_key() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d")


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


def enforce_document_rate_limit(request: Request, scope: str) -> JSONResponse | None:
    limiter = document_upload_rate_limiter if scope == "documents_upload" else document_answer_rate_limiter
    result = limiter.check(request, scope)
    if result.allowed:
        return None

    request_id = getattr(request.state, "request_id", None)
    log_event(
        logger,
        "rate_limited",
        module=scope,
        request_id=request_id,
        client_ip=result.client_ip,
        retry_after_seconds=result.retry_after_seconds,
    )

    user_message = (
        "Too many PDF uploads from this connection right now. Please wait a moment and try again."
        if scope == "documents_upload"
        else "Too many document questions from this connection right now. Please wait a moment and try again."
    )

    return JSONResponse(
        status_code=429,
        headers={"Retry-After": str(result.retry_after_seconds)},
        content={"detail": user_message},
    )


def enforce_usage_quota(
    db: Session,
    *,
    auth_context: AuthContext,
    scope: str,
    request_id: str | None,
) -> JSONResponse | None:
    limit = FREE_TIER_LIMITS.get(scope)
    if not limit or not auth_context.is_authenticated:
        return None

    used = crud.count_usage(
        db,
        user_id=auth_context.user_id,
        scope=scope,
        period_key=_daily_period_key(),
    )
    if used < limit:
        return None

    log_event(
        logger,
        "usage_quota_exceeded",
        module=scope,
        request_id=request_id,
        user_id=auth_context.user_id,
        quota_limit=limit,
        quota_used=used,
    )
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Your current free-tier limit for this workflow is used up for today. Please come back tomorrow or upgrade when subscriptions launch."
        },
    )


def record_usage_event(
    db: Session,
    *,
    auth_context: AuthContext,
    scope: str,
    amount: int = 1,
) -> None:
    crud.record_usage(
        db,
        user_id=auth_context.user_id,
        session_id=auth_context.session_id,
        scope=scope,
        amount=amount,
        period_key=_daily_period_key(),
    )


def find_cached_response(
    db: Session,
    *,
    module: str,
    user_id: str,
    query: str,
    request_id: str | None,
) -> CachedResponseMatch | None:
    cached = crud.get_cached_search(db, module=module, user_id=user_id, query=query)
    cache_mode = "exact"

    if not cached:
        cached = crud.get_similar_cached_search(db, module=module, user_id=user_id, query=query)
        cache_mode = "similar" if cached else "miss"

    log_event(
        logger,
        "cache_hit" if cached else "cache_miss",
        module=module,
        request_id=request_id,
        cache_mode=cache_mode if cached else "miss",
    )
    return CachedResponseMatch(response=cached, mode=cache_mode) if cached else None


def should_use_emergency_fallback() -> bool:
    provider_status = get_provider_status()
    return provider_status["provider_error_category"] in {
        "quota_exceeded",
        "no_validated_generation_model",
        "provider_5xx",
    } or provider_status["provider_recovery_state"] == "cooldown"


def get_fallback_stream_source() -> str:
    provider_status = get_provider_status()
    if provider_status["provider_recovery_state"] in {"recovering", "degraded", "cooldown", "probing"}:
        return "recovering"
    return "fallback"


def trigger_provider_recovery_if_needed() -> bool:
    return request_provider_recovery()


def get_runtime_diagnostics() -> dict[str, int]:
    return {
        "requests_per_minute": ai_rate_limiter.recent_request_count(),
        "document_uploads_per_minute": document_upload_rate_limiter.recent_request_count(),
        "document_answers_per_minute": document_answer_rate_limiter.recent_request_count(),
        **get_stream_observability(),
    }
