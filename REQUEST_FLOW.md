# Scholr Request Flow

## 1. Current AI Module Flow

```mermaid
sequenceDiagram
    participant U as Student
    participant F as Next.js frontend
    participant B as FastAPI backend
    participant R as Rate limiter
    participant C as Cache check
    participant G as Gemini provider
    participant D as History DB

    U->>F: Submit Research / Notes / Doubt prompt
    F->>B: POST /api/{module}
    B->>R: Check per-IP rate limit
    R-->>B: allow or 429
    B->>C: Check short-TTL cache
    alt cache hit
        C-->>B: cached response
        B-->>F: SSE chunk replay
    else cache miss
        C-->>B: no cached response
        B->>G: Start Gemini streaming
        G-->>B: streamed chunks
        B-->>F: JSON-safe SSE chunks
        B->>D: Save completed response
    end
    B-->>F: data: [DONE]
    F-->>U: Render output + copy / clear / retry
```

## 2. Current Frontend Rendering Flow

1. The student opens Research, Notes, or Doubt.
2. The shared module page sends a request to the shared API client.
3. The frontend parses SSE events incrementally.
4. Output updates live while generation is still in flight.
5. If an error occurs, the page shows a category-aware retry state.

## 3. Current Reliability Controls

- request IDs on every backend request
- structured logs
- in-memory rate limiting
- short-TTL cache replay
- provider startup validation
- runtime model fallback
- history-save isolation

## 4. Document Intelligence Scaffold Flow

```mermaid
sequenceDiagram
    participant U as Student
    participant F as Future upload UI
    participant B as FastAPI documents router
    participant P as PDF parser
    participant V as Vector store
    participant G as Gemini embeddings / answer layer

    U->>F: Upload PDF
    F->>B: POST /api/documents/upload
    B->>P: Extract readable text
    P-->>B: Pages
    B->>B: Chunk content with overlap
    B->>V: Store chunk vectors + metadata
    B-->>F: document_id + retrieval readiness

    U->>F: Ask grounded question
    F->>B: POST /api/documents/answer
    B->>V: Retrieve relevant chunks
    V-->>B: Top-k chunks with citation labels
    B->>G: Generate grounded answer
    G-->>B: Citation-aware response
    B-->>F: Answer + citations/snippets
```

## 5. Why This Flow Matters

Scholr's defensibility will come from turning generic AI access into:

- repeatable academic workflows
- grounded document understanding
- citation-aware output
- reusable history and memory

That is the difference between a useful student product and a generic chat wrapper.
