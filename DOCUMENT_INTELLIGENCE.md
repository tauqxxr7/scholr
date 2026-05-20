# Scholr Document Intelligence

This document audits the current backend-only PDF and retrieval foundation.

## Current routes

- `POST /api/documents/upload`
- `POST /api/documents/answer`

## Upload flow

1. accept PDF upload
2. enforce 10 MB file size limit
3. parse readable text from the PDF
4. chunk text with overlap
5. store document metadata and chunk metadata
6. create embeddings
7. upsert vectors into ChromaDB
8. return document status and warnings

## Retrieval flow

1. embed question
2. query top chunks
3. build citation-rich context
4. attempt provider-backed grounded answer
5. if provider unavailable, fall back to deterministic retrieval evidence

## Citation-grounded answer target

The intended answer format is:
- direct answer first
- short grounded explanation second
- cited snippets third
- language like `According to Page 4...` or `From the uploaded document...`

## Current dependencies

- `pypdf`
- `chromadb`
- `python-multipart`
- Google GenAI embeddings path

## Current safeguards

- upload size limit
- temp file cleanup
- gitignored local document and vector directories
- citation metadata preserved per chunk
- warning path if embeddings are unavailable

## Known limitations

- no frontend upload experience yet
- no per-user document ownership
- local vector storage is not a final production data path
- provider-backed document answers still depend on external model availability
- no dedicated PYQ intelligence workflow yet

## Future PYQ intelligence lane

Once the base RAG path is stable, Scholr can extend document intelligence toward previous-year-question support:

- ingest PYQ PDFs
- detect repeated themes and question clusters
- map questions to likely topics
- generate citation-grounded revision hints
- keep PYQ intelligence separate from generic PDF chat so the student value proposition stays sharp

## Future pgvector migration

The most natural long-term production migration is:
- PostgreSQL for durable metadata
- `pgvector` for embeddings and similarity search
- auth-gated document ownership

## Security and privacy concerns

- uploaded files may contain sensitive educational material
- retention and deletion policies need to be explicit before broad release
- auth is required before multi-user document intelligence can be treated as production complete
