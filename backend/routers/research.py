from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from agents.research_agent import generate_research_response
from db import crud
from db.database import get_db
from models.schemas import ResearchRequest
from routers._streaming import build_sse_response

router = APIRouter()


@router.post("/research")
async def research_endpoint(request: ResearchRequest, db: Session = Depends(get_db)):
    return build_sse_response(
        generator=generate_research_response(request.topic),
        save_history=lambda response: crud.save_search(
            db=db,
            module="research",
            query=request.topic,
            response=response,
        ),
        empty_message="Scholr could not find a usable research response for that topic. Try making the topic more specific.",
    )
