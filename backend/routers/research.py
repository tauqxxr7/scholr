from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from agents.research_agent import generate_research_response
from db import crud
from db.database import get_db
from models.schemas import ResearchRequest
from routers._streaming import sse_json_stream

router = APIRouter()


@router.post("/research")
async def research_endpoint(request: ResearchRequest, db: Session = Depends(get_db)):
    async def stream_response():
        full_response: list[str] = []
        try:
            async for chunk in generate_research_response(request.topic):
                full_response.append(chunk)
                yield chunk
        except Exception as exc:
            yield f"\n\n**Error generating research:** {exc}\n\nPlease try again."
        finally:
            if full_response:
                crud.save_search(
                    db=db,
                    module="research",
                    query=request.topic,
                    response="".join(full_response),
                )

    return StreamingResponse(
        sse_json_stream(stream_response()),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
