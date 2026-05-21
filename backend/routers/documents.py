import logging
from time import perf_counter

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from starlette.datastructures import UploadFile as StarletteUploadFile

from core.logging_utils import log_event
from db.database import get_db
from models.schemas import (
    DocumentAnswerRequest,
    DocumentAnswerResponse,
    DocumentUploadResponse,
)
from routers._runtime import enforce_document_rate_limit
from services.document_rag import DocumentIntelligenceError, answer_from_document, ingest_document

router = APIRouter()
logger = logging.getLogger("scholr.documents")


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    request: Request,
    db: Session = Depends(get_db),
):
    started_at = perf_counter()
    request_id = getattr(request.state, "request_id", None)
    rate_limited_response = enforce_document_rate_limit(request, "documents_upload")
    if rate_limited_response is not None:
        return rate_limited_response
    try:
        form = await request.form()
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Multipart form parsing is not available yet. Install python-multipart to enable PDF upload.",
        ) from exc

    file = form.get("file")
    if file is None:
        raise HTTPException(status_code=400, detail="A PDF file field named 'file' is required.")
    if not isinstance(file, StarletteUploadFile):
        raise HTTPException(status_code=400, detail="The uploaded file payload is invalid.")

    try:
        payload, warning = await ingest_document(file, db)
        log_event(
            logger,
            "document_upload_completed",
            request_id=request_id,
            filename=file.filename,
            page_count=payload["page_count"],
            chunk_count=payload["chunk_count"],
            retrieval_ready=payload["retrieval_ready"],
            status=payload["status"],
            duration_ms=round((perf_counter() - started_at) * 1000),
        )
        return DocumentUploadResponse(**payload, warning=warning)
    except DocumentIntelligenceError as exc:
        log_event(
            logger,
            "document_upload_failed",
            request_id=request_id,
            filename=getattr(file, "filename", None),
            error_category=exc.category,
            duration_ms=round((perf_counter() - started_at) * 1000),
        )
        raise HTTPException(status_code=400, detail=exc.message) from exc


@router.post("/documents/answer", response_model=DocumentAnswerResponse)
async def answer_document_question(
    http_request: Request,
    request: DocumentAnswerRequest,
    db: Session = Depends(get_db),
):
    started_at = perf_counter()
    request_id = getattr(http_request.state, "request_id", None)
    rate_limited_response = enforce_document_rate_limit(http_request, "documents_answer")
    if rate_limited_response is not None:
        return rate_limited_response
    try:
        payload = await answer_from_document(
            document_id=request.document_id,
            question=request.question,
            db=db,
            top_k=request.top_k,
        )
        log_event(
            logger,
            "document_answer_completed",
            request_id=request_id,
            document_id=request.document_id,
            retrieval_mode=payload["retrieval_mode"],
            answer_mode=payload["answer_mode"],
            generation_used=payload["generation_used"],
            citations_count=len(payload["citations"]),
            duration_ms=round((perf_counter() - started_at) * 1000),
        )
        return DocumentAnswerResponse(**payload)
    except DocumentIntelligenceError as exc:
        log_event(
            logger,
            "document_answer_failed",
            request_id=request_id,
            document_id=request.document_id,
            error_category=exc.category,
            duration_ms=round((perf_counter() - started_at) * 1000),
        )
        raise HTTPException(status_code=400, detail=exc.message) from exc
