from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from agents._generation import build_provider_degraded_text
from agents.notes_agent import generate_notes_response
from db import crud
from db.database import get_db
from models.schemas import NotesRequest
from routers._runtime import enforce_rate_limit, find_cached_response, should_use_emergency_fallback
from routers._streaming import build_sse_response, stream_text_chunks

router = APIRouter()


@router.post("/notes")
async def notes_endpoint(
    request: NotesRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    rate_limit_response = enforce_rate_limit(http_request, "notes")
    if rate_limit_response:
        return rate_limit_response

    request_id = getattr(http_request.state, "request_id", None)
    cached = find_cached_response(
        db,
        module="notes",
        query=request.topic,
        request_id=request_id,
    )
    use_fallback = should_use_emergency_fallback() and not cached

    return build_sse_response(
        generator=stream_text_chunks(cached.response.response)
        if cached
        else stream_text_chunks(build_provider_degraded_text("notes", request.topic))
        if use_fallback
        else generate_notes_response(request.topic),
        save_history=lambda response: crud.save_search(
            db=db,
            module="notes",
            query=request.topic,
            response=response,
        ),
        empty_message="Scholr could not turn that topic into notes this time. Try a clearer exam topic or concept name.",
        request=http_request,
        module="notes",
        source="warm_cache" if cached and cached.mode == "similar" else "cache" if cached else "fallback" if use_fallback else "live",
    )
