from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResearchRequest(BaseModel):
    topic: str
    mode: str | None = None
    response_mode: str = "fast"


class NotesRequest(BaseModel):
    topic: str
    response_mode: str = "fast"


class DoubtRequest(BaseModel):
    question: str
    subject: str | None = None
    response_mode: str = "fast"


class FeedbackRequest(BaseModel):
    module: str
    query: str
    rating: str
    response_length: int
    mode: str | None = None
    latency_ms: int | None = None


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
    document_name: str
    page_number: int
    chunk_index: int
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
    answer_mode: str
    retrieval_mode: str
    confidence: str
    limitations: list[str]
    warning: str | None = None
