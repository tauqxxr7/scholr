from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from agents.notes_agent import generate_notes_response
from db import crud
from db.database import get_db
from models.schemas import NotesRequest
from routers._streaming import sse_json_stream

router = APIRouter()


@router.post("/notes")
async def notes_endpoint(request: NotesRequest, db: Session = Depends(get_db)):
    async def stream_response():
        full_response: list[str] = []
        try:
            async for chunk in generate_notes_response(request.topic):
                full_response.append(chunk)
                yield chunk
        except Exception as exc:
            yield f"\n\n**Error generating notes:** {exc}\n\nPlease try again."
        finally:
            if full_response:
                crud.save_search(
                    db=db,
                    module="notes",
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
