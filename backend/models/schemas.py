from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ResearchRequest(BaseModel):
    topic: str
    user_id: Optional[str] = None


class NotesRequest(BaseModel):
    topic: str
    user_id: Optional[str] = None


class DoubtRequest(BaseModel):
    question: str
    subject: Optional[str] = None
    user_id: Optional[str] = None


class SearchHistoryItem(BaseModel):
    id: str
    module: str
    query: str
    response: str
    created_at: datetime

    class Config:
        from_attributes = True
