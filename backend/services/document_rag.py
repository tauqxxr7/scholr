import shutil
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path

import google.generativeai as genai
from fastapi import UploadFile
from sqlalchemy.orm import Session

from agents._generation import ScholrGenerationError, stream_gemini_response
from db import crud

MAX_DOCUMENT_SIZE_BYTES = 10 * 1024 * 1024
DEFAULT_CHUNK_SIZE = 1200
DEFAULT_CHUNK_OVERLAP = 180
DEFAULT_TOP_K = 4
EMBEDDING_MODEL_NAME = "models/text-embedding-004"
DOCUMENTS_ROOT = Path("data/documents")
VECTOR_DB_ROOT = Path("data/chromadb")
DOCUMENT_COLLECTION_NAME = "scholr_documents"


class DocumentIntelligenceError(Exception):
    def __init__(self, message: str, *, category: str = "document_intelligence"):
        super().__init__(message)
        self.message = message
        self.category = category


@dataclass
class RetrievedChunk:
    page_number: int
    citation_label: str
    snippet: str


def _safe_title(filename: str) -> str:
    stem = Path(filename).stem.strip()
    return stem[:120] if stem else "Uploaded document"


def _safe_storage_name(filename: str) -> str:
    suffix = Path(filename).suffix or ".pdf"
    return f"{uuid.uuid4().hex}{suffix}"


def _ensure_storage_dirs() -> None:
    DOCUMENTS_ROOT.mkdir(parents=True, exist_ok=True)
    VECTOR_DB_ROOT.mkdir(parents=True, exist_ok=True)


def _load_pdf_reader():
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise DocumentIntelligenceError(
            "PDF parsing dependency is not installed. Add pypdf before using document upload.",
            category="missing_dependency",
        ) from exc
    return PdfReader


def _load_chroma_client():
    try:
        import chromadb
    except ImportError as exc:
        raise DocumentIntelligenceError(
            "Vector store dependency is not installed. Add chromadb before using semantic retrieval.",
            category="missing_dependency",
        ) from exc

    return chromadb.PersistentClient(path=str(VECTOR_DB_ROOT))


async def _read_upload_bytes(upload: UploadFile) -> bytes:
    content = await upload.read()
    if not content:
        raise DocumentIntelligenceError("The uploaded PDF is empty.", category="empty_upload")
    if len(content) > MAX_DOCUMENT_SIZE_BYTES:
        raise DocumentIntelligenceError(
            "PDF uploads are currently limited to 10 MB for MVP safety.",
            category="file_too_large",
        )
    return content


def _extract_pdf_pages(pdf_path: Path) -> list[dict[str, int | str]]:
    PdfReader = _load_pdf_reader()
    reader = PdfReader(str(pdf_path))
    pages: list[dict[str, int | str]] = []

    for page_index, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if text:
            pages.append({"page_number": page_index, "text": text})

    if not pages:
        raise DocumentIntelligenceError(
            "No readable text could be extracted from that PDF. Try a text-based PDF instead of scanned pages.",
            category="unreadable_pdf",
        )

    return pages


def _chunk_page_text(pages: list[dict[str, int | str]]) -> list[dict[str, int | str]]:
    chunks: list[dict[str, int | str]] = []

    for page in pages:
        page_number = int(page["page_number"])
        text = str(page["text"])
        start = 0
        chunk_index = 0

        while start < len(text):
            end = min(start + DEFAULT_CHUNK_SIZE, len(text))
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append(
                    {
                        "page_number": page_number,
                        "chunk_index": chunk_index,
                        "content": chunk_text,
                        "citation_label": f"Page {page_number}",
                    }
                )
                chunk_index += 1

            if end >= len(text):
                break
            start = max(end - DEFAULT_CHUNK_OVERLAP, start + 1)

    if not chunks:
        raise DocumentIntelligenceError(
            "The PDF was parsed, but Scholr could not produce usable chunks for retrieval.",
            category="chunking_failed",
        )

    return chunks


def _embed_texts(texts: list[str], *, task_type: str) -> list[list[float]]:
    try:
        result = genai.embed_content(
            model=EMBEDDING_MODEL_NAME,
            content=texts,
            task_type=task_type,
        )
    except Exception as exc:  # pragma: no cover - provider path depends on runtime access
        raise DocumentIntelligenceError(
            "Embeddings could not be generated for this document right now.",
            category="embedding_provider_error",
        ) from exc

    embeddings = result.get("embedding") if isinstance(result, dict) else None
    if embeddings and isinstance(embeddings, list) and embeddings and isinstance(embeddings[0], float):
        return [embeddings]

    if isinstance(embeddings, list):
        return embeddings

    raise DocumentIntelligenceError(
        "Embeddings returned in an unexpected format.",
        category="embedding_provider_error",
    )


def _upsert_chunks_into_vector_store(document_id: str, chunks: list[dict[str, int | str]]) -> None:
    client = _load_chroma_client()
    collection = client.get_or_create_collection(name=DOCUMENT_COLLECTION_NAME)
    texts = [str(chunk["content"]) for chunk in chunks]
    embeddings = _embed_texts(texts, task_type="retrieval_document")

    collection.upsert(
        ids=[f"{document_id}:{index}" for index in range(len(chunks))],
        documents=texts,
        embeddings=embeddings,
        metadatas=[
            {
                "document_id": document_id,
                "page_number": int(chunk["page_number"]),
                "citation_label": str(chunk["citation_label"]),
                "chunk_index": int(chunk["chunk_index"]),
            }
            for chunk in chunks
        ],
    )


async def ingest_document(upload: UploadFile, db: Session) -> tuple[dict[str, int | str | bool], str | None]:
    if upload.content_type not in {"application/pdf", "application/octet-stream"}:
        raise DocumentIntelligenceError(
            "Only PDF uploads are supported in the current document intelligence scaffold.",
            category="invalid_file_type",
        )

    _ensure_storage_dirs()
    warning: str | None = None
    raw_bytes = await _read_upload_bytes(upload)
    storage_name = _safe_storage_name(upload.filename or "document.pdf")
    document_path = DOCUMENTS_ROOT / storage_name

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(raw_bytes)
        temp_path = Path(temp_file.name)

    try:
        pages = _extract_pdf_pages(temp_path)
        chunks = _chunk_page_text(pages)
        shutil.move(str(temp_path), document_path)
    finally:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)

    record = crud.create_document_asset(
        db,
        title=_safe_title(upload.filename or "document.pdf"),
        original_filename=upload.filename or "document.pdf",
        storage_path=str(document_path),
        mime_type=upload.content_type or "application/pdf",
    )
    crud.save_document_chunks(db, document_id=record.id, chunks=chunks)

    retrieval_ready = True
    try:
        _upsert_chunks_into_vector_store(record.id, chunks)
    except DocumentIntelligenceError as exc:
        retrieval_ready = False
        warning = exc.message

    crud.update_document_asset_status(
        db,
        document_id=record.id,
        status="ready" if retrieval_ready else "stored_without_embeddings",
        page_count=len(pages),
        chunk_count=len(chunks),
    )

    return (
        {
            "document_id": record.id,
            "title": record.title,
            "status": "ready" if retrieval_ready else "stored_without_embeddings",
            "page_count": len(pages),
            "chunk_count": len(chunks),
            "retrieval_ready": retrieval_ready,
        },
        warning,
    )


def retrieve_document_chunks(
    *,
    document_id: str,
    query: str,
    db: Session,
    top_k: int = DEFAULT_TOP_K,
) -> list[RetrievedChunk]:
    _ensure_storage_dirs()
    document = crud.get_document_asset(db, document_id)
    if not document:
        raise DocumentIntelligenceError("Document not found.", category="document_not_found")

    client = _load_chroma_client()
    collection = client.get_or_create_collection(name=DOCUMENT_COLLECTION_NAME)
    embeddings = _embed_texts([query], task_type="retrieval_query")
    result = collection.query(
        query_embeddings=embeddings,
        n_results=max(1, min(top_k, 8)),
        where={"document_id": document_id},
    )

    documents = result.get("documents", [[]])
    metadatas = result.get("metadatas", [[]])
    if not documents or not documents[0]:
        raise DocumentIntelligenceError(
            "No relevant document chunks were found for that question yet.",
            category="no_retrieval_results",
        )

    retrieved: list[RetrievedChunk] = []
    for snippet, metadata in zip(documents[0], metadatas[0], strict=False):
        retrieved.append(
            RetrievedChunk(
                page_number=int(metadata.get("page_number", 1)),
                citation_label=str(metadata.get("citation_label", "Uploaded document")),
                snippet=str(snippet),
            )
        )

    return retrieved


def _fallback_citation_answer(question: str, retrieved: list[RetrievedChunk]) -> str:
    bullet_points = "\n".join(
        f"- According to {chunk.citation_label}, {chunk.snippet[:220].strip()}"
        for chunk in retrieved[:3]
    )
    return (
        f"Scholr could not run a full citation-aware generation for this question right now.\n\n"
        f"Question: {question}\n\n"
        f"Most relevant document evidence:\n{bullet_points}"
    )


async def answer_from_document(
    *,
    document_id: str,
    question: str,
    db: Session,
    top_k: int = DEFAULT_TOP_K,
) -> dict[str, object]:
    retrieved = retrieve_document_chunks(document_id=document_id, query=question, db=db, top_k=top_k)
    context = "\n\n".join(
        f"{chunk.citation_label}: {chunk.snippet}"
        for chunk in retrieved
    )
    prompt = f"""
You are Scholr, an academic document intelligence assistant.

Use only the cited document context below to answer the student's question.
If the evidence is incomplete, say that clearly.
Reference citations inline like "According to Page 4..." and keep the answer grounded in the uploaded PDF.

Question: {question}

Document context:
{context}
"""

    try:
        collected: list[str] = []
        async for chunk in stream_gemini_response(
            model_name="gemini-1.5-flash",
            prompt=prompt,
            temperature=0.2,
            max_output_tokens=1024,
        ):
            collected.append(chunk)
        answer = "".join(collected).strip()
        generation_used = True
        warning = None
    except ScholrGenerationError:
        answer = _fallback_citation_answer(question, retrieved)
        generation_used = False
        warning = "Document retrieval succeeded, but provider-backed answer generation is still unavailable."

    return {
        "document_id": document_id,
        "answer": answer,
        "citations": [
            {
                "page_number": chunk.page_number,
                "citation_label": chunk.citation_label,
                "snippet": chunk.snippet[:280],
            }
            for chunk in retrieved
        ],
        "retrieval_ready": True,
        "generation_used": generation_used,
        "warning": warning,
    }
