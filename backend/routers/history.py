from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from core.auth import AuthContext, require_auth_context
from db import crud
from db.database import get_db
from models.schemas import SearchHistoryItem

router = APIRouter()


@router.get("/history/export")
def export_history_csv(db: Session = Depends(get_db)):
    import csv
    import io

    records = crud.get_all_recent_searches(db, limit=1000)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "module", "query", "created_at", "response_length"])
    for record in records:
        writer.writerow(
            [
                record.id,
                record.module,
                record.query,
                record.created_at.isoformat(),
                len(record.response),
            ]
        )
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=scholr-history.csv"},
    )


@router.get("/history", response_model=list[SearchHistoryItem])
def get_history(
    module: Optional[str] = None,
    user_id: Optional[str] = None,
    limit: int = 12,
    page: int = 1,
    db: Session = Depends(get_db),
    auth_context: AuthContext = Depends(require_auth_context),
):
    safe_limit = max(1, min(limit, 50))
    safe_page = max(page, 1)
    effective_user_id = user_id if user_id and user_id != "anonymous" else None

    if module:
        if effective_user_id:
            return crud.get_searches_by_module(
                db,
                module=module,
                user_id=effective_user_id,
                limit=safe_limit,
                page=safe_page,
            )
        return crud.get_all_searches_by_module(
            db,
            module=module,
            limit=safe_limit,
            page=safe_page,
        )
    if effective_user_id:
        return crud.get_recent_searches(db, user_id=effective_user_id, limit=safe_limit, page=safe_page)
    return crud.get_all_recent_searches(db, limit=safe_limit, page=safe_page)
