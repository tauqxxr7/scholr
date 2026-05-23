from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from agents._generation import build_provider_degraded_text
from agents.notes_agent import generate_notes_response
from core.auth import AuthContext, require_auth_context
from db import crud
from db.database import get_db
from models.schemas import NotesRequest
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


@router.post("/notes")
async def notes_endpoint(
    request: NotesRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    auth_context: AuthContext = Depends(require_auth_context),
):
    rate_limit_response = enforce_rate_limit(http_request, "notes")
    if rate_limit_response:
        return rate_limit_response

    request_id = getattr(http_request.state, "request_id", None)
    quota_response = enforce_usage_quota(
        db,
        auth_context=auth_context,
        scope="notes",
        request_id=request_id,
    )
    if quota_response:
        return quota_response
    record_usage_event(db, auth_context=auth_context, scope="notes")
    response_mode = request.response_mode.strip().lower()
    cached = None
    if response_mode != "deep":
        cached = find_cached_response(
            db,
            module="notes",
            user_id=auth_context.user_id,
            query=request.topic,
            request_id=request_id,
        )
    use_fallback = should_use_emergency_fallback() and not cached
    fallback_text = build_provider_degraded_text("notes", request.topic)
    if use_fallback:
        trigger_provider_recovery_if_needed()

    return build_sse_response(
        generator=stream_text_chunks(cached.response.response)
        if cached
        else stream_text_chunks(fallback_text)
        if use_fallback
        else generate_notes_response(request.topic, response_mode),
        save_history=lambda response: crud.save_search(
            db=db,
            module="notes",
            query=request.topic,
            response=response,
            user_id=auth_context.user_id,
            session_id=auth_context.session_id,
        ),
        empty_message="Scholr could not turn that topic into notes this time. Try a clearer exam topic or concept name.",
        request=http_request,
        module="notes",
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
    )
