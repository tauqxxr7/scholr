import re
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from db.database import DocumentAsset, DocumentChunk, SearchHistory


def save_search(db: Session, module: str, query: str, response: str) -> SearchHistory:
    record = SearchHistory(module=module, query=query, response=response)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def normalize_query(query: str) -> str:
    return re.sub(r"\s+", " ", query.strip().lower())


def _query_tokens(query: str) -> set[str]:
    normalized = normalize_query(query)
    return {token for token in re.findall(r"[a-z0-9]+", normalized) if len(token) >= 3}


def _similarity_score(left: str, right: str) -> float:
    left_tokens = _query_tokens(left)
    right_tokens = _query_tokens(right)
    if not left_tokens or not right_tokens:
        return 0.0

    overlap = left_tokens & right_tokens
    if not overlap:
        return 0.0

    union = left_tokens | right_tokens
    return len(overlap) / max(len(union), 1)


def get_recent_searches(db: Session, limit: int = 20, page: int = 1) -> list[SearchHistory]:
    offset = max(page - 1, 0) * limit
    return (
        db.query(SearchHistory)
        .order_by(SearchHistory.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_searches_by_module(
    db: Session,
    module: str,
    limit: int = 20,
    page: int = 1,
) -> list[SearchHistory]:
    offset = max(page - 1, 0) * limit
    return (
        db.query(SearchHistory)
        .filter(SearchHistory.module == module)
        .order_by(SearchHistory.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def get_cached_search(
    db: Session,
    *,
    module: str,
    query: str,
    ttl_minutes: int = 15,
    scan_limit: int = 25,
) -> SearchHistory | None:
    normalized_query = normalize_query(query)
    cutoff = datetime.utcnow() - timedelta(minutes=ttl_minutes)

    recent_rows = (
        db.query(SearchHistory)
        .filter(SearchHistory.module == module, SearchHistory.created_at >= cutoff)
        .order_by(SearchHistory.created_at.desc())
        .limit(scan_limit)
        .all()
    )

    for row in recent_rows:
        if normalize_query(row.query) == normalized_query:
            return row

    return None


def get_similar_cached_search(
    db: Session,
    *,
    module: str,
    query: str,
    ttl_minutes: int = 30,
    scan_limit: int = 40,
    minimum_score: float = 0.55,
) -> SearchHistory | None:
    cutoff = datetime.utcnow() - timedelta(minutes=ttl_minutes)
    recent_rows = (
        db.query(SearchHistory)
        .filter(SearchHistory.module == module, SearchHistory.created_at >= cutoff)
        .order_by(SearchHistory.created_at.desc())
        .limit(scan_limit)
        .all()
    )

    best_match: SearchHistory | None = None
    best_score = 0.0
    for row in recent_rows:
        score = _similarity_score(query, row.query)
        if score >= minimum_score and score > best_score:
            best_match = row
            best_score = score

    return best_match


def create_document_asset(
    db: Session,
    *,
    title: str,
    original_filename: str,
    storage_path: str,
    mime_type: str = "application/pdf",
) -> DocumentAsset:
    record = DocumentAsset(
        title=title,
        original_filename=original_filename,
        storage_path=storage_path,
        mime_type=mime_type,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_document_asset_status(
    db: Session,
    *,
    document_id: str,
    status: str,
    page_count: int | None = None,
    chunk_count: int | None = None,
) -> DocumentAsset | None:
    record = db.query(DocumentAsset).filter(DocumentAsset.id == document_id).first()
    if not record:
        return None

    record.status = status
    if page_count is not None:
        record.page_count = page_count
    if chunk_count is not None:
        record.chunk_count = chunk_count
    record.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(record)
    return record


def save_document_chunks(
    db: Session,
    *,
    document_id: str,
    chunks: list[dict[str, int | str]],
) -> list[DocumentChunk]:
    records = [
        DocumentChunk(
            document_id=document_id,
            page_number=int(chunk["page_number"]),
            chunk_index=int(chunk["chunk_index"]),
            content=str(chunk["content"]),
            citation_label=str(chunk["citation_label"]),
        )
        for chunk in chunks
    ]
    db.add_all(records)
    db.commit()
    for record in records:
        db.refresh(record)
    return records


def get_document_asset(db: Session, document_id: str) -> DocumentAsset | None:
    return db.query(DocumentAsset).filter(DocumentAsset.id == document_id).first()


def get_document_chunks(db: Session, document_id: str) -> list[DocumentChunk]:
    return (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.page_number.asc(), DocumentChunk.chunk_index.asc())
        .all()
    )
