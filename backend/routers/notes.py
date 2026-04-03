from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.schemas import NotesRequest
from agents.notes_agent import generate_notes_response
import json

router = APIRouter()

@router.post("/notes")
async def notes_endpoint(request: NotesRequest):
    async def stream_response():
        async for chunk in generate_notes_response(request.topic):
            data = json.dumps({"chunk": chunk})
            yield f"data: {data}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )
