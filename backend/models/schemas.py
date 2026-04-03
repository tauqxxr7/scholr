from pydantic import BaseModel
from typing import Optional

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

class SearchResponse(BaseModel):
    id: str
    module: str
    query: str
    response: str
    created_at: str
