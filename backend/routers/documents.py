from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from db.database import get_db
from models.schemas import (
    DocumentAnswerRequest,
    DocumentAnswerResponse,
    DocumentUploadResponse,
)
from services.document_rag import DocumentIntelligenceError, answer_from_document, ingest_document

router = APIRouter()


@router.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(
    request: Request,
    db: Session = Depends(get_db),
):
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
    if not isinstance(file, UploadFile):
        raise HTTPException(status_code=400, detail="The uploaded file payload is invalid.")

    try:
        payload, warning = await ingest_document(file, db)
        return DocumentUploadResponse(**payload, warning=warning)
    except DocumentIntelligenceError as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc


@router.post("/documents/answer", response_model=DocumentAnswerResponse)
async def answer_document_question(
    request: DocumentAnswerRequest,
    db: Session = Depends(get_db),
):
    try:
        payload = await answer_from_document(
            document_id=request.document_id,
            question=request.question,
            db=db,
            top_k=request.top_k,
        )
        return DocumentAnswerResponse(**payload)
    except DocumentIntelligenceError as exc:
        raise HTTPException(status_code=400, detail=exc.message) from exc
