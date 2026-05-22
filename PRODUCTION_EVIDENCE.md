# Scholr Production Evidence

## Live endpoints

- Frontend: [https://scholr-coral.vercel.app](https://scholr-coral.vercel.app)
- Backend health: [https://scholr-k9sj.onrender.com/health](https://scholr-k9sj.onrender.com/health)
- Provider health: [https://scholr-k9sj.onrender.com/health/provider](https://scholr-k9sj.onrender.com/health/provider)
- Generation smoke test: [https://scholr-k9sj.onrender.com/health/generate-test](https://scholr-k9sj.onrender.com/health/generate-test)
- Document health: [https://scholr-k9sj.onrender.com/health/documents](https://scholr-k9sj.onrender.com/health/documents)

## Current production evidence table

| Capability | Status | Proof |
| --- | --- | --- |
| Deployment | Live | Vercel frontend + Render backend |
| Mobile responsiveness | Verified by viewport pass | Latest production pass used iPhone/Android/tablet viewport checks; physical-device retest should be recorded separately |
| SSE streaming | Working | Shared FastAPI SSE routes and client stream parser |
| Provider recovery | Active | Provider diagnostics and background validation loop |
| Provider failover | Working | OpenRouter is currently serving validated AI generation when Gemini is quota-blocked |
| Fallback mode | Working | No-empty-output guarantee and fallback academic mode |
| Cache behavior | Working | Exact cache, warm cache, optimistic hydration |
| Document intelligence | Live in retrieval-first mode | Upload UI, cited answers, lexical fallback, PYQ and study workflows |
| User validation | Ready | Templates and research pack present, no fabricated data |
| CI status | Live | Backend CI, Frontend CI, Repo Hygiene passing |

## Current MVP Status

- Public-access MVP: stable and intentionally available without sign-in
- OpenRouter AI generation: active production path while Gemini remains quota/model-access sensitive
- Semantic retrieval: supported when embedding and vector-store health are ready
- Lexical fallback: preserved for grounded document answers if semantic retrieval degrades
- Auth: postponed until a custom domain and auth plan are ready
- PostgreSQL/pgvector: next infrastructure step for persistent multi-user storage and durable vector retrieval
- Student validation: pending; this repository contains templates only, not fabricated feedback

## Final public MVP verification checklist

| Area | Pass Criteria | Latest Status | Notes |
| --- | --- | --- | --- |
| Landing page | Loads on live Vercel with no mobile horizontal overflow | Passed | Latest pass used responsive viewport checks |
| Dashboard | Opens publicly without auth regression | Passed | `/dashboard` route is public |
| Research | Route loads and SSE stream completes | Passed | Live stream proof recorded through backend probe |
| Notes | Route loads and SSE stream completes | Passed | Live stream proof recorded through backend probe |
| Doubt | Route loads and SSE stream completes | Passed | Live stream proof recorded through backend probe |
| Documents | Route loads, upload works, answers include citations | Passed | Fixture workflow verified |
| Mobile | iPhone/Android/tablet viewport behavior is balanced | Passed by emulation | Physical iPhone retest remains a manual checklist item |
| Desktop | Landing/dashboard remain visually stable | Passed | No desktop route regression observed |
| Provider health | `/health/provider` returns structured status | Passed | OpenRouter active in latest production proof |
| Semantic retrieval | `/health/documents` reports retrieval health honestly | Supported | Semantic depends on embedding/vector health |
| Lexical retrieval | Grounded fallback remains available | Preserved | Required if semantic retrieval degrades |
| SSE streaming | `[DONE]` arrives for AI modules | Passed | Research, Notes, Doubt checked |

## Provider failover proof

Live provider snapshot confirmed on 2026-05-21:

- `provider_ready: true`
- `active_provider: openrouter`
- `selected_model: google/gemini-2.0-flash-lite-001`
- `selected_model_validation_status: validated`
- `provider_recovery_state: active`
- `gemini_provider_ready: false`
- `openrouter_provider_ready: true`

Real output proof files:
- [docs/proof/research-sample.md](docs/proof/research-sample.md)
- [docs/proof/notes-sample.md](docs/proof/notes-sample.md)
- [docs/proof/doubt-sample.md](docs/proof/doubt-sample.md)
- [docs/proof/live-proof.json](docs/proof/live-proof.json)

Visual proof assets:
- [docs/proof/desktop-home-live.png](docs/proof/desktop-home-live.png)
- [docs/proof/desktop-research-live.png](docs/proof/desktop-research-live.png)
- [docs/proof/mobile-notes-live.png](docs/proof/mobile-notes-live.png)
- [docs/proof/mobile-documents-live.png](docs/proof/mobile-documents-live.png)
- [docs/proof/live-stream-proof.png](docs/proof/live-stream-proof.png)
- [docs/proof/provider-proof.png](docs/proof/provider-proof.png)
- [docs/proof/document-proof.png](docs/proof/document-proof.png)

## Live document workflow verification

Verified live against the deployed frontend and backend using the bundled fixture:
- upload fixture: `backend/tests/fixtures/academic-sample.pdf`
- upload result: `ready`
- answer result: `grounded_generation`
- retrieval mode: `semantic`
- citations: present
- no empty output observed
- current live retrieval default: semantic
- embedding provider: `openrouter`
- embedding model: `openai/text-embedding-3-small`
- provider-backed answer synthesis is currently healthy through OpenRouter

## Honest semantic retrieval status

- generation provider failover is healthy
- embedding provider path is healthy through OpenRouter in the latest live check
- semantic retrieval is restored in live production
- lexical retrieval remains the preserved grounded backup if embeddings or vector queries degrade again
- `/health/documents` reports embedding provider, embedding model, embedding latency, vector-store health, retrieval counters, and upload/answer telemetry separately from generation-provider health

## Current runtime truth

- Live MVP: stable
- Gemini provider: degraded by quota, but no longer blocks production usefulness
- OpenRouter provider: currently validated and serving true AI generation
- User-facing experience: functional through AI Mode, cache-backed replay, or fallback academic mode
- Document intelligence: frontend PDF workflow exists and stays honest about retrieval-only vs grounded AI behavior
- Auth status: Clerk/auth is removed from the active app; public access is preserved until custom-domain auth is intentionally reintroduced

## Honest limitation

Scholr's external provider is still susceptible to quota and model access variability. The platform mitigates this with provider diagnostics, recovery, caching, and deterministic academic fallback, but that is not the same as unlimited provider capacity.
