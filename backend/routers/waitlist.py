from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel, EmailStr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.database import Waitlist, get_db
from core.slowapi_limiter import limiter

router = APIRouter()


class WaitlistRequest(BaseModel):
    email: EmailStr
    source: str = "landing_page"


@router.post("/api/waitlist")
@limiter.limit("5/minute")
def join_waitlist(
    request: Request,
    response: Response,
    payload: WaitlistRequest,
    db: Session = Depends(get_db),
):
    del request
    del response
    existing = db.query(Waitlist).filter(Waitlist.email == payload.email).first()
    if existing:
        return {"added": False, "already_registered": True}
    entry = Waitlist(
        id=str(uuid.uuid4()),
        email=payload.email,
        source=payload.source,
        created_at=datetime.utcnow(),
    )
    db.add(entry)
    try:
        db.commit()
        return {"added": True, "already_registered": False}
    except IntegrityError:
        db.rollback()
        return {"added": False, "already_registered": True}
