from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from db.database import Feedback, SearchHistory, get_db

router = APIRouter()


@router.get("/api/metrics")
def get_metrics(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    day_ago = now - timedelta(hours=24)
    week_ago = now - timedelta(days=7)

    total_searches = db.query(func.count(SearchHistory.id)).scalar() or 0
    searches_24h = db.query(func.count(SearchHistory.id)).filter(
        SearchHistory.created_at >= day_ago
    ).scalar() or 0
    searches_7d = db.query(func.count(SearchHistory.id)).filter(
        SearchHistory.created_at >= week_ago
    ).scalar() or 0

    by_module = db.query(
        SearchHistory.module,
        func.count(SearchHistory.id).label('count')
    ).group_by(SearchHistory.module).all()

    total_feedback = db.query(func.count(Feedback.id)).scalar() or 0
    helpful = db.query(func.count(Feedback.id)).filter(
        Feedback.rating == "helpful"
    ).scalar() or 0
    not_helpful = db.query(func.count(Feedback.id)).filter(
        Feedback.rating == "not_helpful"
    ).scalar() or 0

    return {
        "searches": {
            "total": total_searches,
            "last_24h": searches_24h,
            "last_7d": searches_7d,
            "by_module": {row.module: row.count for row in by_module},
        },
        "feedback": {
            "total": total_feedback,
            "helpful": helpful,
            "not_helpful": not_helpful,
            "helpful_rate": round(helpful / total_feedback * 100, 1) if total_feedback > 0 else None,
        },
        "generated_at": now.isoformat(),
    }
