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
- Responsive mobile, tablet, laptop, and desktop layouts
- Clean shared output cards
- loading skeletons
- empty states
- retry states
- copy + clear actions
- markdown rendering that does not crash on streamed output
- public privacy and terms pages
- basic launch metadata, robots, and sitemap assets
- PWA-lite manifest and mobile browser metadata

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
3. Add demo video and a polished repo GIF or walkthrough asset
4. Add CI checks for lint, typecheck, backend validation, and build
5. Reintroduce auth later, only after the wedge proves retention
6. Move production history to PostgreSQL if usage justifies it
7. Expand SEO and legal polish only when the public launch needs become sharper

## Roadmap Extensions

### Auth & security roadmap

- Google OAuth login
- user-specific history
- protected dashboard
- email verification
- password reset only if password auth is introduced
- rate limiting and abuse protection

### API pagination roadmap

- keep `limit` and `page` support simple and stable
- add richer filtering only if real usage demands it

### Logging and observability roadmap

- centralized error logging later with Sentry, Grafana, or Azure Monitor
- no sensitive provider errors exposed in the client console
- request tracing and latency monitoring after usage grows

### Near-term engineering roadmap

- caching repeated prompts where it clearly improves latency
- request IDs for easier debugging across backend flows
- stronger backend log structure for operational visibility
- rate limiting once public usage starts increasing
- keep sanitized error handling as a non-negotiable default

### Analytics roadmap

- start with Vercel Analytics or PostHog later
- keep analytics lightweight and privacy-aware

### SEO roadmap

- Google Search Console
- richer Open Graph previews
- content pages only if distribution needs increase

### Device support roadmap

- keep testing real-device edge cases for iPhone Safari, iPad Safari, and Android Chrome
- add app icons beyond the current placeholder-safe manifest setup
- consider install prompts only if repeat usage justifies a fuller PWA pass

### Legal and compliance roadmap

- iterate privacy and terms as the public rollout expands
- add stronger data-handling language if user accounts are introduced

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
