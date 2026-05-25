from datetime import datetime, timedelta
import os

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from db.database import SearchHistory, get_db

router = APIRouter()


@router.get("/api/status")
def get_status(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    hour_ago = now - timedelta(hours=1)
    recent = (
        db.query(func.count(SearchHistory.id))
        .filter(
            SearchHistory.created_at >= hour_ago,
            SearchHistory.module != "validation_session",
        )
        .scalar()
        or 0
    )

    return {
        "status": "operational",
        "version": os.getenv("APP_VERSION", "1.5.0"),
        "services": {
            "frontend": "operational",
            "backend": "operational",
            "ai_provider": "operational",
            "database": "operational",
        },
        "queries_last_hour": recent,
        "uptime_note": "Render free tier may have ~30s cold start on first request",
        "checked_at": now.isoformat(),
    }
