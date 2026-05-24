from datetime import datetime
import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.database import Waitlist, get_db

router = APIRouter()


class WaitlistRequest(BaseModel):
    email: EmailStr
    source: str = "landing_page"


@router.post("/api/waitlist")
def join_waitlist(request: WaitlistRequest, db: Session = Depends(get_db)):
    existing = db.query(Waitlist).filter(Waitlist.email == request.email).first()
    if existing:
        return {"added": False, "already_registered": True}
    entry = Waitlist(
        id=str(uuid.uuid4()),
        email=request.email,
        source=request.source,
        created_at=datetime.utcnow(),
    )
    db.add(entry)
    try:
        db.commit()
        return {"added": True, "already_registered": False}
    except IntegrityError:
        db.rollback()
        return {"added": False, "already_registered": True}
