# Scholr Progress Blueprint

## Current Stage

Scholr is in the clean MVP stage:
- no auth
- one focused student workflow
- deployment-ready monorepo
- local SQLite support
- production-ready PostgreSQL path through `DATABASE_URL`

## What Is Completed

### Product foundation

- Clean monorepo structure with `frontend/`, `backend/`, and top-level docs
- Landing page, dashboard, research, notes, and doubt routes
- Shared AI module UI instead of duplicated page logic
- Shared frontend API client with production-safe URL handling

### Backend

- FastAPI app in `backend/main.py`
- `GET /health`
- `POST /api/research`
- `POST /api/notes`
- `POST /api/doubt`
- `GET /api/history`
- shared Gemini generation helper
- shared SSE streaming helper
- JSON-safe SSE payloads
- `[DONE]` sent on every stream
- graceful handling for:
  - missing API key
  - invalid Gemini access
  - model/provider failure
  - timeout/network issues
  - history save failure

### Data

- SQLite works locally by default
- full completed responses are saved
- PostgreSQL can be used in production through `DATABASE_URL` without code changes

### Frontend

- Responsive dashboard shell
- Clean shared output cards
- loading skeletons
- empty states
- retry states
- copy + clear actions
- markdown rendering that does not crash on streamed output

### Deployment prep

- Render-ready backend configuration
- Vercel-ready frontend configuration
- env examples for both apps
- repo safety and ignore rules aligned with MVP deployment

## What Is Pending

- deploy backend on Render
- deploy frontend on Vercel
- add live screenshots and demo URLs to README
- verify production smoke test against deployed services

## Next Milestones

1. Finish production deployment
2. Capture screenshots and short demo walkthrough
3. Add CI checks for lint, typecheck, and backend validation
4. Reintroduce auth only after the wedge is stable in production
5. Add per-user history and saved items later

## Deployment Status

- Local development flow: ready
- Backend deployment config: ready for Render
- Frontend deployment config: ready for Vercel
- Production persistence: requires PostgreSQL via `DATABASE_URL`
- Local-only persistence: SQLite

## Azure Future Scaling Idea

If Scholr grows beyond the MVP wedge, the most natural Azure path is:

- Azure OpenAI / Azure AI Foundry for enterprise-grade model routing
- Azure Functions for event-driven background jobs or async processing
- Azure Cosmos DB for globally distributed app data and user history
- Azure AI Search for semantic retrieval across notes, research, and academic content
- Azure Blob Storage for exported files, uploaded documents, and large assets
- Azure API Management for auth, quotas, observability, and partner integrations

That path is intentionally future-facing. It is not needed for the MVP.
