from datetime import datetime, timedelta
from typing import Optional
import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db.database import SearchHistory, get_db

router = APIRouter()


class ValidationSession(BaseModel):
    student_name: Optional[str] = None
    college: Optional[str] = None
    year: Optional[str] = None
    referred_by: Optional[str] = "direct"
    session_id: Optional[str] = None


@router.post("/api/validation/session")
def record_validation_session(session: ValidationSession, db: Session = Depends(get_db)):
    """Record when a real student uses Scholr for the first time."""
    record = SearchHistory(
        id=str(uuid.uuid4()),
        module="validation_session",
        query=f"{session.college or 'unknown'} | {session.year or 'unknown'} | {session.referred_by}",
        response=f"Student: {session.student_name or 'anonymous'}",
        created_at=datetime.utcnow(),
    )
    db.add(record)
    db.commit()
    return {"recorded": True, "session_id": record.id}


@router.get("/api/validation/summary")
def get_validation_summary(db: Session = Depends(get_db)):
    """Summary of real student validation sessions."""
    sessions = db.query(SearchHistory).filter(
        SearchHistory.module == "validation_session"
    ).all()

    week_ago = datetime.utcnow() - timedelta(days=7)
    recent = [s for s in sessions if s.created_at >= week_ago]

    colleges = set()
    for session in sessions:
        parts = session.query.split(" | ")
        if parts and parts[0] != "unknown":
            colleges.add(parts[0])

    return {
        "total_validation_sessions": len(sessions),
        "sessions_last_7_days": len(recent),
        "unique_colleges": list(colleges),
        "college_count": len(colleges),
        "validation_goal": 10,
        "progress_percent": min(round(len(sessions) / 10 * 100), 100),
    }
