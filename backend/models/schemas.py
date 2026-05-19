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


class DocumentUploadResponse(BaseModel):
    document_id: str
    title: str
    status: str
    page_count: int
    chunk_count: int
    retrieval_ready: bool
    warning: str | None = None


class DocumentCitationItem(BaseModel):
    page_number: int
    citation_label: str
    snippet: str


class DocumentAnswerRequest(BaseModel):
    document_id: str
    question: str
    top_k: int = 4


class DocumentAnswerResponse(BaseModel):
    document_id: str
    answer: str
    citations: list[DocumentCitationItem]
    retrieval_ready: bool
    generation_used: bool
    warning: str | None = None
