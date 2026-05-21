# Scholr RAG Roadmap

This document explains the next careful steps from backend scaffold to production-safe document intelligence.

## Current state

- backend document routes exist
- PDF parsing works
- chunking with overlap works
- document metadata and chunk metadata are stored
- embedding-provider abstraction exists when dependencies and provider access are available
- citation-aware answer format exists
- retrieval-only lexical fallback exists
- frontend document upload and question UI exists

## Stepwise roadmap

### Phase 1

- validate the live document workspace with real class notes and research PDFs
- confirm dependency behavior on Render
- verify temp cleanup and error handling
- verify chunk metadata quality
- run the bundled smoke script with the fixture PDF
- define a citation format students can trust

### Phase 2

- refine document status, warning states, and workflow quality in the frontend upload flow
- test citation usefulness with real student documents
- capture proof screenshots for upload, retrieval mode, citations, and mobile document UX
- validate whether question-paper and PYQ workflows should become a dedicated mode instead of generic document Q and A
- validate semantic retrieval separately from generation-provider health
- validate OpenRouter-compatible embedding models without assuming universal support

### Phase 3

- move local vector storage toward `pgvector` or another production-safe store
- stabilize the embedding provider path across Gemini and optional fallback providers
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

## Current honest status

- document workflow is live
- lexical fallback is stable
- grounded answers can still be generated when the active generation provider is healthy
- semantic retrieval is architecture-ready but not yet restored in live production
