from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from agents.doubt_agent import generate_doubt_response
from db import crud
from db.database import get_db
from models.schemas import DoubtRequest
from routers._streaming import sse_json_stream

router = APIRouter()


@router.post("/doubt")
async def doubt_endpoint(request: DoubtRequest, db: Session = Depends(get_db)):
    async def stream_response():
        full_response: list[str] = []
        query = request.question if not request.subject else f"[{request.subject}] {request.question}"
        try:
            async for chunk in generate_doubt_response(request.question, request.subject or "General"):
                full_response.append(chunk)
                yield chunk
        except Exception as exc:
            yield f"\n\n**Error solving doubt:** {exc}\n\nPlease try again."
        finally:
            if full_response:
                crud.save_search(
                    db=db,
                    module="doubt",
                    query=query,
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
