import re
import os
import shutil
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter

from fastapi import UploadFile
from sqlalchemy.orm import Session

from agents._generation import (
    ScholrGenerationError,
    embed_texts,
    get_embedding_provider_status,
    sanitize_user_input,
    stream_gemini_response,
    validate_embedding_provider,
)
from db import crud

MAX_DOCUMENT_SIZE_BYTES = 10 * 1024 * 1024
DEFAULT_CHUNK_SIZE = 1200
DEFAULT_CHUNK_OVERLAP = 180
DEFAULT_TOP_K = 4
DOCUMENTS_ROOT = Path("data/documents")
VECTOR_DB_ROOT = Path("data/chromadb")
DOCUMENT_COLLECTION_NAME = "scholr_documents"
DOCUMENT_OBSERVABILITY: dict[str, int | str | None] = {
    "document_upload_success_count": 0,
    "document_upload_failure_count": 0,
    "document_answer_success_count": 0,
    "document_answer_failure_count": 0,
    "semantic_retrieval_success_count": 0,
    "lexical_retrieval_usage_count": 0,
    "vector_query_failure_count": 0,
    "embedding_generation_failure_count": 0,
    "last_upload_latency_ms": None,
    "last_retrieval_latency_ms": None,
    "last_vector_query_latency_ms": None,
    "last_document_answer_latency_ms": None,
}


def record_document_upload_failure() -> None:
    DOCUMENT_OBSERVABILITY["document_upload_failure_count"] += 1


def record_document_answer_failure() -> None:
    DOCUMENT_OBSERVABILITY["document_answer_failure_count"] += 1


class DocumentIntelligenceError(Exception):
    def __init__(self, message: str, *, category: str = "document_intelligence"):
        super().__init__(message)
        self.message = message
        self.category = category


@dataclass
class RetrievedChunk:
    document_name: str
    page_number: int
    chunk_index: int
    citation_label: str
    snippet: str
    score: float


@dataclass
class RetrievalResult:
    chunks: list[RetrievedChunk]
    retrieval_mode: str
    warning: str | None = None


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


def _module_available(module_name: str) -> bool:
    try:
        __import__(module_name)
    except ImportError:
        return False
    return True


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
                        "document_name": "",
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


def _tokenize_text(value: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9]+", value.lower()) if len(token) >= 3}


def _lexical_score(query: str, content: str) -> float:
    query_tokens = _tokenize_text(query)
    content_tokens = _tokenize_text(content)
    if not query_tokens or not content_tokens:
        return 0.0

    overlap = query_tokens & content_tokens
    if not overlap:
        return 0.0

    return len(overlap) / max(len(query_tokens), 1)


def _retrieve_chunks_from_db(
    *,
    document_id: str,
    query: str,
    db: Session,
    top_k: int,
) -> list[RetrievedChunk]:
    ranked_chunks: list[RetrievedChunk] = []
    for chunk in crud.get_document_chunks(db, document_id):
        score = _lexical_score(query, chunk.content)
        if score <= 0:
            continue
        ranked_chunks.append(
            RetrievedChunk(
                document_name=chunk.document_name,
                page_number=chunk.page_number,
                chunk_index=chunk.chunk_index,
                citation_label=chunk.citation_label,
                snippet=chunk.content,
                score=score,
            )
        )

    ranked_chunks.sort(key=lambda item: (-item.score, item.page_number, item.chunk_index))
    return ranked_chunks[: max(1, min(top_k, 8))]


def _upsert_chunks_into_vector_store(document_id: str, chunks: list[dict[str, int | str]]) -> None:
    client = _load_chroma_client()
    collection = client.get_or_create_collection(name=DOCUMENT_COLLECTION_NAME)
    texts = [str(chunk["content"]) for chunk in chunks]
    try:
        embeddings = embed_texts(texts, task_type="RETRIEVAL_DOCUMENT")
    except ScholrGenerationError as exc:
        DOCUMENT_OBSERVABILITY["embedding_generation_failure_count"] += 1
        raise DocumentIntelligenceError(
            "Embeddings could not be generated for this document right now.",
            category=exc.category,
        ) from exc

    collection.upsert(
        ids=[f"{document_id}:{index}" for index in range(len(chunks))],
        documents=texts,
        embeddings=embeddings,
        metadatas=[
            {
                "document_id": document_id,
                "document_name": str(chunk.get("document_name", "Uploaded document")),
                "page_number": int(chunk["page_number"]),
                "citation_label": str(chunk["citation_label"]),
                "chunk_index": int(chunk["chunk_index"]),
            }
            for chunk in chunks
        ],
    )


async def ingest_document(upload: UploadFile, db: Session) -> tuple[dict[str, int | str | bool], str | None]:
    started_at = perf_counter()
    if upload.content_type not in {"application/pdf", "application/octet-stream"}:
        DOCUMENT_OBSERVABILITY["document_upload_failure_count"] += 1
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
    for chunk in chunks:
        chunk["document_name"] = record.title
    crud.save_document_chunks(db, document_id=record.id, document_name=record.title, chunks=chunks)

    retrieval_ready = True
    status = "ready"
    try:
        _upsert_chunks_into_vector_store(record.id, chunks)
    except DocumentIntelligenceError as exc:
        retrieval_ready = True
        status = "ready_with_lexical_fallback"
        warning = (
            f"{exc.message} Scholr will use retrieval-only lexical grounding for this document until embeddings recover."
        )

    crud.update_document_asset_status(
        db,
        document_id=record.id,
        status=status,
        page_count=len(pages),
        chunk_count=len(chunks),
    )
    DOCUMENT_OBSERVABILITY["document_upload_success_count"] += 1
    DOCUMENT_OBSERVABILITY["last_upload_latency_ms"] = round((perf_counter() - started_at) * 1000)

    return (
        {
            "document_id": record.id,
            "title": record.title,
            "status": status,
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
) -> RetrievalResult:
    started_at = perf_counter()
    _ensure_storage_dirs()
    document = crud.get_document_asset(db, document_id)
    if not document:
        raise DocumentIntelligenceError("Document not found.", category="document_not_found")

    try:
        client = _load_chroma_client()
        collection = client.get_or_create_collection(name=DOCUMENT_COLLECTION_NAME)
    except DocumentIntelligenceError as exc:
        DOCUMENT_OBSERVABILITY["vector_query_failure_count"] += 1
        lexical_chunks = _retrieve_chunks_from_db(document_id=document_id, query=query, db=db, top_k=top_k)
        if not lexical_chunks:
            raise DocumentIntelligenceError(
                "No relevant document chunks were found for that question yet.",
                category="no_retrieval_results",
            ) from exc
        DOCUMENT_OBSERVABILITY["lexical_retrieval_usage_count"] += 1
        DOCUMENT_OBSERVABILITY["last_retrieval_latency_ms"] = round((perf_counter() - started_at) * 1000)
        return RetrievalResult(
            chunks=lexical_chunks,
            retrieval_mode="lexical",
            warning="Vector storage is unavailable right now, so Scholr is using retrieval-only lexical grounding.",
        )
    try:
        embeddings = embed_texts([query], task_type="RETRIEVAL_QUERY")
    except ScholrGenerationError as exc:
        DOCUMENT_OBSERVABILITY["embedding_generation_failure_count"] += 1
        lexical_chunks = _retrieve_chunks_from_db(document_id=document_id, query=query, db=db, top_k=top_k)
        if not lexical_chunks:
            raise DocumentIntelligenceError(
                "No relevant document chunks were found for that question yet.",
                category="no_retrieval_results",
            ) from exc
        DOCUMENT_OBSERVABILITY["lexical_retrieval_usage_count"] += 1
        DOCUMENT_OBSERVABILITY["last_retrieval_latency_ms"] = round((perf_counter() - started_at) * 1000)
        return RetrievalResult(
            chunks=lexical_chunks,
            retrieval_mode="lexical",
            warning="Embedding query path is unavailable, so Scholr is using retrieval-only lexical grounding.",
        )

    vector_query_started_at = perf_counter()
    try:
        result = collection.query(
            query_embeddings=embeddings,
            n_results=max(1, min(top_k, 8)),
            where={"document_id": document_id},
        )
    except Exception as exc:
        DOCUMENT_OBSERVABILITY["vector_query_failure_count"] += 1
        DOCUMENT_OBSERVABILITY["last_vector_query_latency_ms"] = round((perf_counter() - vector_query_started_at) * 1000)
        lexical_chunks = _retrieve_chunks_from_db(document_id=document_id, query=query, db=db, top_k=top_k)
        if not lexical_chunks:
            raise DocumentIntelligenceError(
                "No relevant document chunks were found for that question yet.",
                category="no_retrieval_results",
            ) from exc
        DOCUMENT_OBSERVABILITY["lexical_retrieval_usage_count"] += 1
        DOCUMENT_OBSERVABILITY["last_retrieval_latency_ms"] = round((perf_counter() - started_at) * 1000)
        return RetrievalResult(
            chunks=lexical_chunks,
            retrieval_mode="lexical",
            warning="Vector retrieval is unavailable right now, so Scholr is using retrieval-only lexical grounding.",
        )
    DOCUMENT_OBSERVABILITY["last_vector_query_latency_ms"] = round((perf_counter() - vector_query_started_at) * 1000)

    documents = result.get("documents", [[]])
    metadatas = result.get("metadatas", [[]])
    if not documents or not documents[0]:
        lexical_chunks = _retrieve_chunks_from_db(document_id=document_id, query=query, db=db, top_k=top_k)
        if not lexical_chunks:
            raise DocumentIntelligenceError(
                "No relevant document chunks were found for that question yet.",
                category="no_retrieval_results",
            )
        DOCUMENT_OBSERVABILITY["lexical_retrieval_usage_count"] += 1
        DOCUMENT_OBSERVABILITY["last_retrieval_latency_ms"] = round((perf_counter() - started_at) * 1000)
        return RetrievalResult(
            chunks=lexical_chunks,
            retrieval_mode="lexical",
            warning="Semantic retrieval returned nothing useful, so Scholr fell back to lexical grounding.",
        )

    retrieved: list[RetrievedChunk] = []
    for snippet, metadata in zip(documents[0], metadatas[0], strict=False):
        retrieved.append(
            RetrievedChunk(
                document_name=str(metadata.get("document_name", document.title)),
                page_number=int(metadata.get("page_number", 1)),
                chunk_index=int(metadata.get("chunk_index", 0)),
                citation_label=str(metadata.get("citation_label", "Uploaded document")),
                snippet=str(snippet),
                score=1.0,
            )
        )

    DOCUMENT_OBSERVABILITY["semantic_retrieval_success_count"] += 1
    DOCUMENT_OBSERVABILITY["last_retrieval_latency_ms"] = round((perf_counter() - started_at) * 1000)
    return RetrievalResult(chunks=retrieved, retrieval_mode="semantic")


def _fallback_citation_answer(question: str, retrieved: list[RetrievedChunk]) -> str:
    bullet_points = "\n".join(
        f"- According to {chunk.document_name}, {chunk.citation_label}, chunk {chunk.chunk_index}, {chunk.snippet[:220].strip()}"
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
    started_at = perf_counter()
    safe_question, warning_prefix = sanitize_user_input("documents", question)
    retrieval = retrieve_document_chunks(document_id=document_id, query=safe_question, db=db, top_k=top_k)
    retrieved = retrieval.chunks
    context = "\n\n".join(
        f"{chunk.document_name} | {chunk.citation_label} | chunk {chunk.chunk_index}: {chunk.snippet}"
        for chunk in retrieved
    )
    prompt = f"""
You are Scholr, an academic document intelligence assistant.

Use only the cited document context below to answer the student's question.
If the evidence is incomplete, say that clearly.
Reference citations inline like "According to {retrieved[0].document_name if retrieved else 'the uploaded document'}, Page 4..." and keep the answer grounded in the uploaded PDF.

Question: {safe_question}

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
        answer_mode = "grounded_generation"
        warning = retrieval.warning
    except ScholrGenerationError:
        answer = _fallback_citation_answer(safe_question, retrieved)
        generation_used = False
        answer_mode = "retrieval_only"
        warning = (
            retrieval.warning
            or "Document retrieval succeeded, but provider-backed answer generation is still unavailable."
        )

    if warning_prefix:
        warning = f"{warning_prefix} {warning}" if warning else warning_prefix

    confidence = "high" if generation_used and len(retrieved) >= 2 else "medium" if len(retrieved) >= 2 else "low"
    limitations = [
        "Answers are grounded only in the uploaded document chunks retrieved for this question.",
    ]
    if answer_mode == "retrieval_only":
        limitations.append("Provider-backed synthesis is currently unavailable, so Scholr is returning retrieval-only academic guidance.")
    if retrieval.retrieval_mode != "semantic":
        limitations.append("Semantic vector retrieval was unavailable, so a lexical chunk match was used instead.")

    DOCUMENT_OBSERVABILITY["document_answer_success_count"] += 1
    DOCUMENT_OBSERVABILITY["last_document_answer_latency_ms"] = round((perf_counter() - started_at) * 1000)

    return {
        "document_id": document_id,
        "answer": answer,
        "citations": [
            {
                "document_name": chunk.document_name,
                "page_number": chunk.page_number,
                "chunk_index": chunk.chunk_index,
                "citation_label": chunk.citation_label,
                "snippet": chunk.snippet[:280],
            }
            for chunk in retrieved
        ],
        "retrieval_ready": True,
        "generation_used": generation_used,
        "answer_mode": answer_mode,
        "retrieval_mode": retrieval.retrieval_mode,
        "confidence": confidence,
        "limitations": limitations,
        "warning": warning,
    }


def get_document_intelligence_health() -> dict[str, object]:
    _ensure_storage_dirs()

    pdf_parsing_available = _module_available("pypdf")
    multipart_available = _module_available("multipart")
    embedding_status = validate_embedding_provider()

    try:
        _load_chroma_client()
        vector_store_available = True
    except DocumentIntelligenceError:
        vector_store_available = False

    embedding_provider_configured = bool(embedding_status["embedding_provider_configured"])
    embedding_provider_ready = bool(embedding_status["embedding_provider_ready"])
    embedding_provider = embedding_status["embedding_provider"]
    embedding_model = embedding_status["embedding_model"]
    provider_error_category = embedding_status["embedding_error_category"]

    if not embedding_provider_configured:
        embedding_health = "provider_unavailable"
    elif not vector_store_available:
        embedding_health = "vector_unavailable"
    elif not embedding_provider_ready:
        embedding_health = "provider_degraded"
    else:
        embedding_health = "ready"

    semantic_retrieval_ready = bool(vector_store_available and embedding_provider_ready)
    lexical_fallback_ready = True
    retrieval_default_mode = "semantic" if semantic_retrieval_ready else "lexical"
    retrieval_health = "healthy" if retrieval_default_mode == "semantic" else "degraded_lexical_fallback"

    vector_store_health = "ready" if vector_store_available else "unavailable"

    return {
        "pdf_parsing_available": pdf_parsing_available,
        "multipart_available": multipart_available,
        "vector_store_available": vector_store_available,
        "vector_store_health": vector_store_health,
        "embedding_provider_configured": embedding_provider_configured,
        "embedding_provider_ready": embedding_provider_ready,
        "provider_ready_for_embeddings": embedding_provider_ready,
        "embedding_provider": embedding_provider,
        "embedding_model": embedding_model,
        "embedding_latency_ms": embedding_status["embedding_latency_ms"],
        "semantic_retrieval_ready": semantic_retrieval_ready,
        "lexical_fallback_ready": lexical_fallback_ready,
        "provider_error_category": provider_error_category,
        "embedding_health": embedding_health,
        "retrieval_health": retrieval_health,
        "retrieval_default_mode": retrieval_default_mode,
        "semantic_retrieval_success_count": DOCUMENT_OBSERVABILITY["semantic_retrieval_success_count"],
        "lexical_retrieval_usage_count": DOCUMENT_OBSERVABILITY["lexical_retrieval_usage_count"],
        "vector_query_failure_count": DOCUMENT_OBSERVABILITY["vector_query_failure_count"],
        "embedding_generation_failure_count": DOCUMENT_OBSERVABILITY["embedding_generation_failure_count"],
        "document_upload_success_count": DOCUMENT_OBSERVABILITY["document_upload_success_count"],
        "document_upload_failure_count": DOCUMENT_OBSERVABILITY["document_upload_failure_count"],
        "document_answer_success_count": DOCUMENT_OBSERVABILITY["document_answer_success_count"],
        "document_answer_failure_count": DOCUMENT_OBSERVABILITY["document_answer_failure_count"],
        "last_upload_latency_ms": DOCUMENT_OBSERVABILITY["last_upload_latency_ms"],
        "last_retrieval_latency_ms": DOCUMENT_OBSERVABILITY["last_retrieval_latency_ms"],
        "last_vector_query_latency_ms": DOCUMENT_OBSERVABILITY["last_vector_query_latency_ms"],
        "last_document_answer_latency_ms": DOCUMENT_OBSERVABILITY["last_document_answer_latency_ms"],
        "documents_storage_path": str(DOCUMENTS_ROOT),
        "vector_storage_path": str(VECTOR_DB_ROOT),
    }
