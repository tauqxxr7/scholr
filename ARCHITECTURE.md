# Scholr Architecture

## Positioning

Scholr is an academic intelligence platform for BTech students. The live architecture is intentionally lean: a responsive Next.js frontend, a FastAPI backend, provider-aware SSE streaming, multi-provider generation recovery, fallback academic generation, lightweight persistence, and a staged backend-first document intelligence layer.

## High-Level Diagram

```mermaid
flowchart LR
    U["Student user"] --> F["Next.js App Router frontend"]
    F -->|"HTTPS + SSE"| M["Runtime mode detector"]
    M --> B["FastAPI backend"]
    B --> G["Validated provider abstraction"]
    B --> E["Embedding provider abstraction"]
    B --> A["Fallback academic engine"]
    B --> C["History + exact cache + warm cache"]
    B --> H["History persistence"]
    B --> L["Structured logs + request IDs + rate limiting + telemetry"]
    H --> S["SQLite (local) or PostgreSQL (production)"]
    B --> D["Document intelligence backend"]
    D --> V["ChromaDB today / pgvector later"]
    G --> GP["Gemini primary"]
    G --> OR["OpenRouter fallback"]
    E --> GE["Gemini embeddings primary"]
    E --> EO["Optional embedding override"]
    E --> LF["Lexical fallback always available"]
    G --> B
    A --> B
    C --> B
```

## Live Runtime Modes

- **AI Mode**: a validated provider-model pair is healthy and Scholr streams live generation
- **OpenRouter AI Mode**: the current live failover path when Gemini generation is quota-blocked but OpenRouter is healthy
- **Cached Academic Response**: an exact or similar recent answer is replayed to protect quota and lower latency
- **Fallback Academic Mode**: the provider is degraded, but Scholr still streams deterministic academic guidance
- **Provider Recovering**: the frontend remains useful while background re-validation tries to restore AI Mode
- **Document Retrieval Mode**: document answers explicitly report whether they came from lexical, semantic, or future hybrid retrieval

## Frontend Responsibilities

- collect prompts for Research, Notes, and Doubt
- collect PDF uploads and document-grounded study questions
- call the backend using `NEXT_PUBLIC_API_URL`
- parse SSE chunks safely across desktop and mobile browsers
- expose copy, clear, retry, and mode-badge feedback
- render optimistic loading, cache hydration, and fallback scaffolds so the UI never feels stalled

## Backend Responsibilities

- assign request IDs and structured logs
- protect Gemini quota with rate limiting
- validate provider capability before promoting a model
- validate provider failover from Gemini to OpenRouter before dropping into academic fallback
- validate embedding capability separately from generation capability
- stream JSON-safe SSE output
- replay exact and warm-cache responses
- save history without blocking the response path
- keep fallback academic output available when the provider is degraded
- surface retrieval mode, citations, confidence, and limitations for document answers

## Current Request Lifecycle

```mermaid
flowchart TD
    Start["Student submits prompt"] --> Rate["Rate limiter"]
    Rate --> Cache{"Exact or warm cache hit?"}
    Cache -->|Yes| Replay["Replay cached response over SSE"]
    Cache -->|No| Provider{"Validated provider ready?"}
    Provider -->|Yes| AI["Stream real Gemini generation"]
    Provider -->|No| Fallback["Stream fallback academic structure"]
    Replay --> Save["Save history if needed"]
    AI --> Save
    Fallback --> Save
    Save --> Done["Emit data: [DONE]"]
```

## Reliability Layers

- validated provider-state cache with lower-cost rechecks
- cooldown-aware retry jitter and background recovery
- Fallback Academic Mode
- Cached Academic Response mode
- no-empty-output guarantee
- request IDs and categorized provider errors
- exact and warm-cache replay
- history-save isolation so successful responses are not lost
- mobile-safe stream parsing and runtime mode badges

## Provider Recovery Strategy

- strict priority chain for provider validation
- primary provider: Gemini
- secondary provider: OpenRouter
- real generation probe before a model becomes active
- degraded mode remains student-safe while background recovery keeps retrying
- cooldown prevents wasteful repeated probes during quota exhaustion
- `/health/provider` and `/health/generate-test` expose safe diagnostics without leaking secrets

## Embedding Provider Strategy

- default embedding provider: Gemini embeddings
- optional override through `EMBEDDING_PROVIDER` and `EMBEDDING_MODEL`
- semantic retrieval is only marked ready when vector storage and embedding validation are both healthy
- lexical fallback remains available even when semantic retrieval is degraded

## Data Layer

- SQLite by default for local development
- PostgreSQL in production through `DATABASE_URL`
- history stores completed responses for replay and review
- document assets and chunks are persisted for backend-first PDF intelligence
- vector storage is local today and intentionally gitignored
- generation-provider readiness and embedding-provider readiness are intentionally independent
- `/health/documents` exposes PDF, multipart, vector, and embedding readiness without exposing secrets
- `/health/documents` truthfully reports whether live document retrieval is currently defaulting to lexical or semantic mode

## Document Intelligence Flow

```mermaid
flowchart TD
    P["Uploaded PDF"] --> X["Text extraction"]
    X --> K["Chunking with overlap"]
    K --> E["Embeddings when available"]
    E --> V["Vector store"]
    K --> L["Lexical fallback index from stored chunks"]
    Q["Student question"] --> R["Retriever"]
    V --> R
    L --> R
    R --> A["Grounded answer or retrieval-only response"]
    A --> O["Answer + cited sources + confidence + limitations"]
```

## Future PYQ Intelligence Extension

```mermaid
flowchart TD
    PYQ["Previous year question PDFs"] --> PX["Parsing and cleanup"]
    PX --> PK["Chunking + metadata"]
    PK --> PV["Vector + keyword index"]
    Student["Student topic or question"] --> PR["Retriever + pattern matcher"]
    PV --> PR
    PR --> PH["Question cluster hints"]
    PR --> PA["Citation-grounded academic answer"]
```

This remains a planning lane, not a live student-facing feature yet.

## Retrieval Modes

- `lexical`: live-safe fallback when semantic retrieval is unavailable
- `semantic`: embedding-backed retrieval when the embedding provider and vector path are both healthy
- `hybrid`: future combination of lexical and semantic scoring

## Deployment

- Frontend: Vercel
- Backend: Render
- Live frontend: `https://scholr-coral.vercel.app`
- Live backend health: `https://scholr-k9sj.onrender.com/health`
- Live provider health: `https://scholr-k9sj.onrender.com/health/provider`
