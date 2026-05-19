# Scholr System Design

## Design Goals

- fast academic workflows for BTech students
- reliable streaming output
- low operational complexity for an MVP
- safe production defaults without overengineering

## Core User Journey

1. Student opens Research, Notes, or Doubt.
2. Student enters one topic or question.
3. Scholr streams structured output in under a minute.
4. Student copies the answer or returns later from dashboard history.

## Current System Components

### 1. Presentation layer

- Next.js App Router
- shared workspace component
- responsive navigation for phone, tablet, and desktop

### 2. Application layer

- FastAPI routing
- prompt shaping per module
- streaming helper shared across all AI routes

### 3. Provider layer

- Gemini API through `google-generativeai`
- startup provider validation
- runtime model fallback across safe supported candidates
- categorized provider diagnostics

### 4. Persistence layer

- history table for completed responses
- SQLite locally
- PostgreSQL-ready in production

### 5. Control layer

- in-memory IP rate limiting
- request IDs
- structured logs
- short-TTL cache replay

## Why SSE

Scholr uses Server-Sent Events instead of waiting for one large final payload because:

- streamed output feels much faster for students
- long notes and research responses stay readable as they arrive
- frontend can distinguish chunk, empty, error, and done states

## Cache Strategy

Current cache strategy is intentionally narrow:

- source: existing history table
- key: normalized prompt + module
- window: 15 minutes
- scope: successful responses only

This keeps Gemini usage and latency under control without introducing Redis before demand exists.

## Rate Limiting Strategy

Current rate limiting is a simple per-IP in-memory limiter:

- 10 requests per minute
- only AI endpoints are protected
- `/health` is not rate-limited

This is good enough for a single-instance MVP and clearly marked for replacement with Redis or a platform-native control later.

## Future Elite Differentiator: Document Intelligence

This is roadmap-only for now.

### Phase 1

- PDF upload
- metadata extraction
- file ownership and storage model

### Phase 2

- chunking
- embeddings
- document index

### Phase 3

- citations from uploaded files inside Notes, Research, and Doubt
- semantic search over both uploaded documents and saved history

### Phase 4

- answer grounding
- confidence hints
- course-pack workflows

