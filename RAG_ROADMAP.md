# Scholr RAG Roadmap

This document explains the next careful steps from backend scaffold to production-safe document intelligence.

## Current state

- backend document routes exist
- PDF parsing scaffold exists
- chunking exists
- embeddings path exists
- retrieval path exists
- citation-aware answer format exists
- frontend upload UI is intentionally not built yet

## Stepwise roadmap

### Phase 1

- validate upload route with real class notes and research PDFs
- confirm dependency behavior on Render
- verify temp cleanup and error handling
- verify chunk metadata quality

### Phase 2

- add secure frontend upload flow
- expose document status and warning states
- test citation usefulness with real student documents

### Phase 3

- move local vector storage toward `pgvector` or another production-safe store
- add document ownership and auth
- add semantic search over history and uploaded content

## Target answer format

- grounded answer
- inline citation language like `According to Page 4...`
- snippet evidence
- warning when retrieval is weak or incomplete

## Non-goals right now

- full RAG chat UI
- arbitrary file ingestion
- large-scale document memory
- multi-tenant document sharing
