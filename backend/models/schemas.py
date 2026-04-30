from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResearchRequest(BaseModel):
    topic: str


class NotesRequest(BaseModel):
    topic: str


class DoubtRequest(BaseModel):
    question: str
    subject: str | None = None


class SearchHistoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    module: str
    query: str
    response: str
    created_at: datetime
