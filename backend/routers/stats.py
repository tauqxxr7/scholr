from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from db.database import Feedback, SearchHistory, get_db

router = APIRouter()


@router.get("/api/stats")
def get_public_stats(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    week_ago = now - timedelta(days=7)

    total_ai_queries = db.query(func.count(SearchHistory.id)).filter(
        SearchHistory.module.notin_(["validation_session", "feedback_form"])
    ).scalar() or 0
    queries_this_week = db.query(func.count(SearchHistory.id)).filter(
        SearchHistory.created_at >= week_ago,
        SearchHistory.module.notin_(["validation_session", "feedback_form"]),
    ).scalar() or 0
    total_feedback = db.query(func.count(Feedback.id)).scalar() or 0
    helpful_feedback = db.query(func.count(Feedback.id)).filter(
        Feedback.rating == "helpful"
    ).scalar() or 0

    return {
        "total_ai_queries": total_ai_queries,
        "queries_this_week": queries_this_week,
        "total_feedback": total_feedback,
        "helpful_feedback": helpful_feedback,
        "generated_at": now.isoformat(),
    }
