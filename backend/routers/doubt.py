from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from agents._generation import build_provider_degraded_text
from agents.doubt_agent import generate_doubt_response
from db import crud
from db.database import get_db
from models.schemas import DoubtRequest
from routers._runtime import enforce_rate_limit, find_cached_response, should_use_emergency_fallback
from routers._streaming import build_sse_response, stream_text_chunks

router = APIRouter()


@router.post("/doubt")
async def doubt_endpoint(
    request: DoubtRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    rate_limit_response = enforce_rate_limit(http_request, "doubt")
    if rate_limit_response:
        return rate_limit_response

    query = request.question if not request.subject else f"[{request.subject}] {request.question}"
    request_id = getattr(http_request.state, "request_id", None)
    cached = find_cached_response(
        db,
        module="doubt",
        query=query,
        request_id=request_id,
    )
    use_fallback = should_use_emergency_fallback() and not cached
    fallback_text = build_provider_degraded_text("doubt", request.question, subject=request.subject or "General")

    return build_sse_response(
        generator=stream_text_chunks(cached.response.response)
        if cached
        else stream_text_chunks(fallback_text)
        if use_fallback
        else generate_doubt_response(request.question, request.subject or "General"),
        save_history=lambda response: crud.save_search(
            db=db,
            module="doubt",
            query=query,
            response=response,
        ),
        empty_message="Scholr could not produce a doubt explanation for that prompt. Try adding more detail or a subject.",
        request=http_request,
        module="doubt",
        source="warm_cache" if cached and cached.mode == "similar" else "cache" if cached else "fallback" if use_fallback else "live",
        recovery_text=fallback_text,
    )
