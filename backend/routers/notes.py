from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from agents.notes_agent import generate_notes_response
from db import crud
from db.database import get_db
from models.schemas import NotesRequest
from routers._streaming import build_sse_response

router = APIRouter()


@router.post("/notes")
async def notes_endpoint(request: NotesRequest, db: Session = Depends(get_db)):
    return build_sse_response(
        generator=generate_notes_response(request.topic),
        save_history=lambda response: crud.save_search(
            db=db,
            module="notes",
            query=request.topic,
            response=response,
        ),
        empty_message="Scholr could not turn that topic into notes this time. Try a clearer exam topic or concept name.",
    )
