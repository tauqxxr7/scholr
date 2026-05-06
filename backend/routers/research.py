from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from agents.research_agent import generate_research_response
from db import crud
from db.database import get_db
from models.schemas import ResearchRequest
from routers._runtime import enforce_rate_limit, find_cached_response
from routers._streaming import build_sse_response, stream_text_chunks

router = APIRouter()


@router.post("/research")
async def research_endpoint(
    request: ResearchRequest,
    http_request: Request,
    db: Session = Depends(get_db),
):
    rate_limit_response = enforce_rate_limit(http_request, "research")
    if rate_limit_response:
        return rate_limit_response

    request_id = getattr(http_request.state, "request_id", None)
    cached = find_cached_response(
        db,
        module="research",
        query=request.topic,
        request_id=request_id,
    )

    return build_sse_response(
        generator=stream_text_chunks(cached.response)
        if cached
        else generate_research_response(request.topic),
        save_history=lambda response: crud.save_search(
            db=db,
            module="research",
            query=request.topic,
            response=response,
        ),
        empty_message="Scholr could not find a usable research response for that topic. Try making the topic more specific.",
        request=http_request,
        module="research",
        source="cache" if cached else "live",
    )
