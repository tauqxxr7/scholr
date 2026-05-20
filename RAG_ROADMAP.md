# Scholr RAG Roadmap

This document explains the next careful steps from backend scaffold to production-safe document intelligence.

## Current state

- backend document routes exist
- PDF parsing works
- chunking with overlap works
- document metadata and chunk metadata are stored
- embeddings path exists when dependencies and provider access are available
- citation-aware answer format exists
- retrieval-only lexical fallback exists
- frontend document upload and question UI exists

## Stepwise roadmap

### Phase 1

- validate upload and retrieval routes with real class notes and research PDFs
- confirm dependency behavior on Render
- verify temp cleanup and error handling
- verify chunk metadata quality
- run the bundled smoke script with the fixture PDF
- define a citation format students can trust

### Phase 2

- refine document status, warning states, and workflow quality in the frontend upload flow
- test citation usefulness with real student documents
- validate whether question-paper and PYQ workflows should become a dedicated mode instead of generic document Q and A

### Phase 3

- move local vector storage toward `pgvector` or another production-safe store
- add document ownership and auth
- add semantic search over history and uploaded content
- add PYQ intelligence later:
  - topic clustering
  - repeated-question pattern detection
  - exam-likelihood hints

## Target answer format

- grounded answer when provider generation is healthy
- retrieval-only answer when provider generation is unavailable
- inline citation language like `According to Page 4...`
- document name, page number, and chunk index in citations
- confidence and limitations so students know how much to trust the result

## Non-goals right now

- full RAG chat UI
- arbitrary file ingestion
- large-scale document memory
- multi-tenant document sharing
- full PYQ productization before the base document pipeline is proven
