from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from agents._generation import build_provider_degraded_text
from agents._validation import RESEARCH_REQUIRED
from agents.research_agent import generate_research_response
from auth.clerk import get_optional_user_id
from core.auth import AuthContext, require_auth_context
from db import crud
from db.database import get_db
from models.schemas import ResearchRequest
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


@router.post("/research")
async def research_endpoint(
    request: ResearchRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    auth_context: AuthContext = Depends(require_auth_context),
    clerk_user_id: str | None = Depends(get_optional_user_id),
):
    rate_limit_response = enforce_rate_limit(http_request, "research")
    if rate_limit_response:
        return rate_limit_response

    request_id = getattr(http_request.state, "request_id", None)
    quota_response = enforce_usage_quota(
        db,
        auth_context=auth_context,
        scope="research",
        request_id=request_id,
    )
    if quota_response:
        return quota_response
    record_usage_event(db, auth_context=auth_context, scope="research")
    effective_user_id = clerk_user_id or "anonymous"
    response_mode = (request.mode or request.response_mode or "fast").strip().lower()
    cached = None
    if response_mode != "deep":
        cached = find_cached_response(
            db,
            module="research",
            user_id=effective_user_id,
            query=request.topic,
            request_id=request_id,
        )
    use_fallback = should_use_emergency_fallback() and not cached
    fallback_text = build_provider_degraded_text("research", request.topic)
    if use_fallback:
        trigger_provider_recovery_if_needed()

    return build_sse_response(
        generator=stream_text_chunks(cached.response.response)
        if cached
        else stream_text_chunks(fallback_text)
        if use_fallback
        else generate_research_response(request.topic, response_mode),
        save_history=lambda response: crud.save_search(
            db=db,
            module="research",
            query=request.topic,
            response=response,
            user_id=effective_user_id,
            session_id=auth_context.session_id,
        ),
        empty_message="Scholr could not find a usable research response for that topic. Try making the topic more specific.",
        request=http_request,
        module="research",
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
        required_sections=RESEARCH_REQUIRED,
        validation_query=request.topic,
    )
