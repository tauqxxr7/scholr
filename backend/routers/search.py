import json

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from agents.embeddings import cosine_similarity, embed_text
from db.database import SearchHistory, get_db

router = APIRouter()


@router.get("/api/search")
def semantic_search(q: str = Query(..., min_length=2), limit: int = 5, db: Session = Depends(get_db)):
    query_embedding = embed_text(q)
    records = db.query(SearchHistory).filter(
        SearchHistory.embedding_json.isnot(None),
        SearchHistory.module != "validation_session",
    ).all()

    scored = []
    for record in records:
        try:
            embedding = json.loads(record.embedding_json)
            score = cosine_similarity(query_embedding, embedding)
            scored.append((score, record))
        except Exception:
            continue

    scored.sort(key=lambda item: item[0], reverse=True)
    results = []
    for score, record in scored[:limit]:
        results.append({
            "id": record.id,
            "module": record.module,
            "query": record.query,
            "score": round(score, 3),
            "created_at": record.created_at.isoformat(),
        })
    return {"query": q, "results": results, "total_searched": len(records)}
