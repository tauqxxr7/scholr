from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.schemas import ResearchRequest
from agents.research_agent import generate_research_response
import json

router = APIRouter()

@router.post("/research")
async def research_endpoint(request: ResearchRequest):
    async def stream_response():
        async for chunk in generate_research_response(request.topic):
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
