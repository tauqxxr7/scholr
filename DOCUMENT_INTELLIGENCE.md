# Scholr Document Intelligence

This document audits the current live PDF workflow and the backend retrieval foundation behind it.

## Current routes

- `POST /api/documents/upload`
- `POST /api/documents/answer`
- `GET /health/documents`

## Upload flow

1. accept PDF upload
2. enforce a 10 MB file size limit
3. parse readable text from the PDF
4. chunk text with overlap
5. store document metadata and chunk metadata
6. attempt embeddings when the provider and vector dependencies are available
7. preserve retrieval-readiness even when semantic indexing is unavailable
8. clean up temporary files
9. expose retrieval-health status safely through `/health/documents`

## Retrieval flow

1. look up the uploaded document and stored chunks
2. try semantic retrieval when embeddings and vector storage are available
3. fall back to lexical retrieval when embeddings or vector storage are unavailable
4. build citation-rich context from the best chunks
5. attempt provider-backed grounded answering
6. fall back to retrieval-only academic evidence when provider generation is unavailable

## Citation-grounded answer target

The current target response shape is:
- `answer`
- `citations`
- `answer_mode`
- `generation_used`
- `confidence`
- `limitations`
- `warning`

Each citation should preserve:
- document name
- page number when available
- chunk index
- citation label
- snippet

Each answer should also expose:
- retrieval mode: `lexical`, `semantic`, or future `hybrid`
- whether provider-backed generation was used
- confidence
- limitations

## Current dependencies

- `pypdf`
- `python-multipart`
- `chromadb`
- Google GenAI embeddings path

## Current safeguards

- upload size limit
- temp file cleanup
- gitignored local document and vector directories
- citation metadata preserved per chunk
- retrieval-only lexical fallback when vector storage is unavailable
- retrieval-only answer fallback when provider generation is unavailable

## Backend validation assets

- smoke script: [backend/scripts/test_documents.py](backend/scripts/test_documents.py)
- bundled fixture: [backend/tests/fixtures/academic-sample.pdf](backend/tests/fixtures/academic-sample.pdf)

The smoke path currently validates:
- upload route
- chunk persistence
- lexical retrieval fallback
- cited response shape
- retrieval mode exposure

## Live verified behavior

Verified against the live Render backend and the live Vercel document workspace:

- PDF upload works with the bundled academic sample fixture
- upload returns `ready_with_lexical_fallback` when embeddings are unavailable
- document answers return:
  - `answer`
  - `citations`
  - `confidence`
  - `limitations`
  - `retrieval_mode`
- live retrieval currently defaults to lexical grounding while the provider remains degraded
- no empty output panels were observed in the live document flow

## Known limitations

- real subject PDFs are not bundled in the repo yet, so DBMS, OS, DSA, CN, Maths, PYQ, and research-paper validation is still pending
- no per-user document ownership
- local vector storage is not a final production data path
- semantic retrieval depends on vector dependencies and model/provider availability
- semantic retrieval health depends on provider-backed embeddings, so live production can truthfully remain in lexical mode during provider degradation

## Future pgvector migration

The most natural long-term production migration is:
- PostgreSQL for durable metadata
- `pgvector` for embeddings and similarity search
- auth-gated document ownership

## Security and privacy concerns

- uploaded files may contain sensitive educational material
- retention and deletion policies need to be explicit before broad release
- auth is required before multi-user document intelligence can be treated as production complete
- document upload remains backend-first until ownership, deletion, and policy flows are clearer
