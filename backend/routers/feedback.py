from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import crud
from db.database import get_db
from models.schemas import FeedbackRequest

router = APIRouter()


@router.post("/feedback")
async def feedback_endpoint(request: FeedbackRequest, db: Session = Depends(get_db)):
    rating = request.rating.strip().lower()
    if rating not in {"helpful", "not_helpful"}:
        raise HTTPException(status_code=400, detail="rating must be helpful or not_helpful")

    crud.save_feedback(
        db=db,
        module=request.module.strip().lower(),
        query=request.query.strip(),
        rating=rating,
        response_length=max(request.response_length, 0),
        mode=request.mode.strip().lower() if request.mode else None,
        latency_ms=max(request.latency_ms, 0) if request.latency_ms is not None else None,
    )
    return {"received": True}
