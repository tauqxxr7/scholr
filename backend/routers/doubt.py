from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.schemas import DoubtRequest
from agents.doubt_agent import generate_doubt_response
import json

router = APIRouter()

@router.post("/doubt")
async def doubt_endpoint(request: DoubtRequest):
    async def stream_response():
        async for chunk in generate_doubt_response(
            request.question,
            request.subject or "General"
        ):
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
