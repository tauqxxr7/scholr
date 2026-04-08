from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from agents.doubt_agent import generate_doubt_response
from db import crud
from db.database import get_db
from models.schemas import DoubtRequest
from routers._streaming import build_sse_response

router = APIRouter()


@router.post("/doubt")
async def doubt_endpoint(request: DoubtRequest, db: Session = Depends(get_db)):
    query = request.question if not request.subject else f"[{request.subject}] {request.question}"

    return build_sse_response(
        generator=generate_doubt_response(request.question, request.subject or "General"),
        save_history=lambda response: crud.save_search(
            db=db,
            module="doubt",
            query=query,
            response=response,
        ),
        empty_message="Scholr could not produce a doubt explanation for that prompt. Try adding more detail or a subject.",
    )
