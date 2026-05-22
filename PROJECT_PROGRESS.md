# Scholr Progress Blueprint

## Current Stage

Scholr is in the stable public-access MVP stage:
- public landing page, dashboard, AI modules, and document workspace are open without sign-in
- OpenRouter AI generation is active as the validated production generation path
- semantic retrieval is supported when embedding/vector diagnostics are healthy
- lexical retrieval fallback is preserved for grounded document answers
- auth is postponed until a custom domain and a clean auth rollout are ready
- PostgreSQL plus pgvector is the next infrastructure phase
- student validation is pending and must use real student data only

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
- in-memory IP rate limiting for AI endpoints
- structured request logging with request IDs
- short-TTL cache replay for repeated prompts
- provider startup validation and runtime model fallback
- warm-cache replay for similar prompts during degraded provider periods
- Fallback Academic Mode for quota exhaustion or missing validated models
- no-empty-output guarantee for Research, Notes, and Doubt
- provider quota observability and cooldown behavior
- pagination-ready history endpoint with `limit` and `page`
- document upload and citation-aware RAG scaffold routes

### Data

- SQLite works locally by default
- full completed responses are saved with user and session context
- user sessions and usage ledgers are persisted
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
- env-gated PostHog analytics wrapper
- safe product events for open, generate, copy, clear, and retry flows
- subtle response-mode badges for AI Mode, Cached Academic Response, and Fallback Academic Mode
- public dashboard and module access without sign-in friction

### Deployment prep

- Render-ready backend configuration
- Render primary and fallback deployment options documented
- Vercel-ready frontend configuration
- env examples for both apps
- repo safety and ignore rules aligned with MVP deployment
- proof package folders for desktop, mobile, and demo capture
- CI workflows for backend, frontend, and repo hygiene
- production evidence and metrics docs
- legal ownership and disclaimer docs
- document intelligence audit and roadmap docs

## Live URLs

- Frontend: [https://scholr-coral.vercel.app](https://scholr-coral.vercel.app)
- Backend health: [https://scholr-k9sj.onrender.com/health](https://scholr-k9sj.onrender.com/health)

## What Is Pending

- run the final public MVP verification checklist after each production deploy
- verify long-term production history persistence with PostgreSQL
- replace placeholder demo GIF and placeholder mobile proof assets with real captures
- keep tenant-safe persistence groundwork inactive until a future auth rollout is intentionally reintroduced
- complete real student validation without fabricated scores or quotes

## Next Milestones

1. Run user validation with 10 to 15 BTech students
2. Review analytics signal after the first student validation sprint
3. Capture polished proof screenshots and a real walkthrough GIF only from actual product state
4. Keep CI checks green for lint, typecheck, backend validation, and build
5. Validate provider fallback behavior under real student usage
6. Reintroduce multi-user auth only after PostgreSQL and persistent user storage are ready
7. Move production history to PostgreSQL if usage justifies it
8. Expand SEO and legal polish only when the public launch needs become sharper
9. Validate document intelligence scaffold with real PDFs before frontend integration

## Roadmap Extensions

### Auth & security roadmap

- Google OAuth login
- user-specific history
- protected dashboard
- email verification
- password reset only if password auth is introduced
- rate limiting and abuse protection
- tenant-safe document ownership and session isolation

### API pagination roadmap

- keep `limit` and `page` support simple and stable
- add richer filtering only if real usage demands it

### Logging and observability roadmap

- centralized error logging later with Sentry, Grafana, or Azure Monitor
- no sensitive provider errors exposed in the client console
- request tracing and latency monitoring after usage grows

### Near-term engineering roadmap

- evaluate whether the 15-minute cache window should stay, shrink, or become Redis-backed
- structured backend log shipping for operational visibility
- stronger rate limiting once public usage starts increasing
- keep sanitized error handling as a non-negotiable default
- continue hardening multi-provider abstraction and usage governance as real traffic grows

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
- Production status:
  - frontend loads
  - backend `/health` works
  - Live MVP is stable
  - OpenRouter AI generation is active in the latest production proof loop
  - Gemini provider can still be degraded due to quota/model access
  - Research / Notes / Doubt remain functional through AI Mode, cache, or Fallback Academic Mode
  - desktop and mobile viewport usage are functional
  - proof package, legal docs, CI workflows, and production evidence docs are now part of the repo surface
  - latest mobile responsiveness fix was verified through viewport emulation; physical-device iPhone retesting should be recorded separately
- Production persistence: requires PostgreSQL via `DATABASE_URL`
- Local-only persistence: SQLite

## Final Public MVP Verification Checklist

| Surface / System | Required Check | Status |
| --- | --- | --- |
| Landing page | live route, responsive mobile layout, no auth requirement | ready for recurring verification |
| Dashboard | public route opens and cards render | ready for recurring verification |
| Research | route opens, SSE stream completes, retry UX intact | ready for recurring verification |
| Notes | route opens, SSE stream completes, formatting intact | ready for recurring verification |
| Doubt | route opens, SSE stream completes, explanation quality acceptable | ready for recurring verification |
| Documents | upload works, answer returns citations, retrieval mode shown | ready for recurring verification |
| Mobile | iPhone SE/13/14, Android, tablet viewport checks | ready for recurring verification |
| Desktop | landing and dashboard do not regress | ready for recurring verification |
| Provider health | `/health/provider` reports active provider honestly | ready for recurring verification |
| Semantic retrieval | `/health/documents` reports semantic readiness honestly | ready for recurring verification |
| Lexical retrieval | fallback remains available when semantic path degrades | ready for recurring verification |
| SSE streaming | `[DONE]` arrives and malformed stream handling remains tolerant | ready for recurring verification |

## Azure Future Scaling Idea

Tauqeer has Azure for Startups access with `$1,000` in credits, but Scholr should stay on Render + Vercel until user validation proves stronger demand.

If Scholr grows beyond the MVP wedge, the most natural Azure path is:

- Azure App Service or Azure Container Apps for backend hosting
- Azure Database for PostgreSQL for durable production history
- Azure AI Search for semantic retrieval across notes, research, and academic content
- Azure Blob Storage for exported files, uploaded documents, and large assets
- Azure Monitor / Application Insights for observability
- Azure OpenAI / Azure AI Foundry for enterprise-grade model routing

That path is intentionally future-facing. It is not needed for the MVP.
