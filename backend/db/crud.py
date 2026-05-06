import re
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from db.database import SearchHistory


def save_search(db: Session, module: str, query: str, response: str) -> SearchHistory:
    record = SearchHistory(module=module, query=query, response=response)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def normalize_query(query: str) -> str:
    return re.sub(r"\s+", " ", query.strip().lower())


def get_recent_searches(db: Session, limit: int = 20, page: int = 1) -> list[SearchHistory]:
    offset = max(page - 1, 0) * limit
    return (
        db.query(SearchHistory)
        .order_by(SearchHistory.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_searches_by_module(
    db: Session,
    module: str,
    limit: int = 20,
    page: int = 1,
) -> list[SearchHistory]:
    offset = max(page - 1, 0) * limit
    return (
        db.query(SearchHistory)
        .filter(SearchHistory.module == module)
        .order_by(SearchHistory.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_cached_search(
    db: Session,
    *,
    module: str,
    query: str,
    ttl_minutes: int = 15,
    scan_limit: int = 25,
) -> SearchHistory | None:
    normalized_query = normalize_query(query)
    cutoff = datetime.utcnow() - timedelta(minutes=ttl_minutes)

    recent_rows = (
        db.query(SearchHistory)
        .filter(SearchHistory.module == module, SearchHistory.created_at >= cutoff)
        .order_by(SearchHistory.created_at.desc())
        .limit(scan_limit)
        .all()
    )

    for row in recent_rows:
        if normalize_query(row.query) == normalized_query:
            return row

    return None
