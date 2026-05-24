from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from agents._generation import build_provider_degraded_text
from agents._validation import DOUBT_REQUIRED
from agents.doubt_agent import generate_doubt_response
from auth.clerk import get_optional_user_id
from cache.response_cache import response_cache
from core.auth import AuthContext, require_auth_context
from core.slowapi_limiter import limiter
from db import crud
from db.database import get_db
from models.schemas import DoubtRequest
from routers._runtime import (
    enforce_rate_limit,
    enforce_usage_quota,
    find_cached_response,
    get_fallback_stream_source,
    record_usage_event,
    should_use_emergency_fallback,
    trigger_provider_recovery_if_needed,
)
from routers._streaming import build_sse_response, stream_text_chunks

router = APIRouter()


@router.post("/doubt")
@limiter.limit("20/minute")
async def doubt_endpoint(
    request: Request,
    payload: DoubtRequest,
    db: Session = Depends(get_db),
    auth_context: AuthContext = Depends(require_auth_context),
    clerk_user_id: str | None = Depends(get_optional_user_id),
):
    rate_limit_response = enforce_rate_limit(request, "doubt")
    if rate_limit_response:
        return rate_limit_response

    query = payload.question if not payload.subject else f"[{payload.subject}] {payload.question}"
    request_id = getattr(request.state, "request_id", None)
    quota_response = enforce_usage_quota(
        db,
        auth_context=auth_context,
        scope="doubt",
        request_id=request_id,
    )
    if quota_response:
        return quota_response
    record_usage_event(db, auth_context=auth_context, scope="doubt")
    effective_user_id = clerk_user_id or "anonymous"
    response_mode = payload.response_mode.strip().lower()
    memory_cached = response_cache.get("doubt", query, response_mode)
    if memory_cached:
        return build_sse_response(
            generator=stream_text_chunks(memory_cached),
            save_history=lambda response: crud.save_search(
                db=db,
                module="doubt",
                query=query,
                response=response,
                user_id=effective_user_id,
                session_id=auth_context.session_id,
            ),
            empty_message="Scholr could not produce a doubt explanation for that prompt. Try adding more detail or a subject.",
            request=request,
            module="doubt",
            mode=response_mode,
            source="cache",
            cache_hit=True,
            required_sections=DOUBT_REQUIRED,
            validation_query=payload.question,
        )

    cached = None
    if response_mode != "deep":
        cached = find_cached_response(
            db,
            module="doubt",
            user_id=effective_user_id,
            query=query,
            request_id=request_id,
        )
    use_fallback = should_use_emergency_fallback() and not cached
    fallback_text = build_provider_degraded_text("doubt", payload.question, subject=payload.subject or "General")
    if use_fallback:
        trigger_provider_recovery_if_needed()

    return build_sse_response(
        generator=stream_text_chunks(cached.response.response)
        if cached
        else stream_text_chunks(fallback_text)
        if use_fallback
        else generate_doubt_response(payload.question, payload.subject or "General", response_mode),
        save_history=lambda response: crud.save_search(
            db=db,
            module="doubt",
            query=query,
            response=response,
            user_id=effective_user_id,
            session_id=auth_context.session_id,
        ),
        empty_message="Scholr could not produce a doubt explanation for that prompt. Try adding more detail or a subject.",
        request=request,
        module="doubt",
        mode=response_mode,
        source="warm_cache"
        if cached and cached.mode == "similar"
        else "cache"
        if cached
        else get_fallback_stream_source()
        if use_fallback
        else "live",
        cache_hit=bool(cached),
        recovery_text=fallback_text,
        required_sections=DOUBT_REQUIRED,
        validation_query=payload.question,
        on_complete=lambda response: response_cache.set("doubt", query, response_mode, response),
    )
