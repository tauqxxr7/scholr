from sqlalchemy.orm import Session

from db.database import SearchHistory


def save_search(db: Session, module: str, query: str, response: str) -> SearchHistory:
    record = SearchHistory(module=module, query=query, response=response)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_recent_searches(db: Session, limit: int = 20) -> list[SearchHistory]:
    return (
        db.query(SearchHistory)
        .order_by(SearchHistory.created_at.desc())
        .limit(limit)
        .all()
    )


def get_searches_by_module(db: Session, module: str, limit: int = 20) -> list[SearchHistory]:
    return (
        db.query(SearchHistory)
        .filter(SearchHistory.module == module)
        .order_by(SearchHistory.created_at.desc())
        .limit(limit)
        .all()
    )
