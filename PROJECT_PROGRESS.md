# Scholr Progress Blueprint

## Current Stage

Scholr is in the live MVP stage:
- no auth
- one focused student workflow
- deployed monorepo
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
- pagination-ready history endpoint with `limit` and `page`

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
- public privacy and terms pages
- basic launch metadata, robots, and sitemap assets

### Deployment prep

- Render-ready backend configuration
- Render primary and fallback deployment options documented
- Vercel-ready frontend configuration
- env examples for both apps
- repo safety and ignore rules aligned with MVP deployment

## Live URLs

- Frontend: [https://scholr-coral.vercel.app](https://scholr-coral.vercel.app)
- Backend health: [https://scholr-k9sj.onrender.com/health](https://scholr-k9sj.onrender.com/health)

## What Is Pending

- add demo video or short walkthrough
- verify long-term production history persistence with PostgreSQL
- capture or generate a short demo GIF for the repo hero section

## Next Milestones

1. Run user validation with 10 BTech students
2. Add light analytics and usage instrumentation
3. Add CI checks for lint, typecheck, backend validation, and build
4. Reintroduce auth later, only after the wedge proves retention
5. Move production history to PostgreSQL if usage justifies it
6. Expand SEO and legal polish only when the public launch needs become sharper

## Deployment Status

- Local development flow: ready
- Backend deployed on Render
- Frontend deployed on Vercel
- Final production smoke test: passed
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
