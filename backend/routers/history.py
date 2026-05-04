from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db import crud
from db.database import get_db
from models.schemas import SearchHistoryItem

router = APIRouter()


@router.get("/history", response_model=list[SearchHistoryItem])
def get_history(
    module: Optional[str] = None,
    limit: int = 12,
    page: int = 1,
    db: Session = Depends(get_db),
):
    safe_limit = max(1, min(limit, 50))
    safe_page = max(page, 1)

    if module:
        return crud.get_searches_by_module(
            db,
            module=module,
            limit=safe_limit,
            page=safe_page,
        )
    return crud.get_recent_searches(db, limit=safe_limit, page=safe_page)
