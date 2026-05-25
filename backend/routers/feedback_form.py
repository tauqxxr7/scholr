from datetime import datetime
from typing import Optional
import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db.database import get_db, SearchHistory

router = APIRouter()


class FeedbackFormRequest(BaseModel):
    name: Optional[str] = None
    college_year: Optional[str] = None
    module_used: Optional[str] = None
    was_useful: Optional[str] = None
    what_was_missing: Optional[str] = None
    would_use_again: Optional[str] = None
    other_feedback: Optional[str] = None


@router.post("/api/feedback-form")
def submit_feedback_form(data: FeedbackFormRequest, db: Session = Depends(get_db)):
    summary = (
        f"useful:{data.was_useful}|again:{data.would_use_again}|module:{data.module_used}|"
        f"missing:{data.what_was_missing or 'none'}|other:{data.other_feedback or 'none'}"
    )
    record = SearchHistory(
        id=str(uuid.uuid4()),
        module="feedback_form",
        query=f"{data.name or 'anonymous'} | {data.college_year or 'unknown'}",
        response=summary,
        created_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    return {"submitted": True}
