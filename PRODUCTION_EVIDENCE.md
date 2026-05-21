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
| Mobile responsiveness | Verified | iOS/manual verification and responsive workspace shell |
| SSE streaming | Working | Shared FastAPI SSE routes and client stream parser |
| Provider recovery | Active | Provider diagnostics and background validation loop |
| Provider failover | Working | OpenRouter is currently serving validated AI generation when Gemini is quota-blocked |
| Fallback mode | Working | No-empty-output guarantee and fallback academic mode |
| Cache behavior | Working | Exact cache, warm cache, optimistic hydration |
| Document intelligence | Live in retrieval-first mode | Upload UI, cited answers, lexical fallback, PYQ and study workflows |
| User validation | Ready | Templates and research pack present, no fabricated data |
| CI status | Live | Backend CI, Frontend CI, Repo Hygiene passing |

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
- upload result: `ready_with_lexical_fallback`
- answer result: `grounded_generation`
- retrieval mode: `lexical`
- citations: present
- no empty output observed
- current live retrieval default: lexical while provider-backed embeddings remain degraded
- provider-backed answer synthesis is still possible through OpenRouter when generation is healthy

## Honest semantic retrieval status

- generation provider failover is healthy
- embedding provider path is still degraded
- semantic retrieval is not yet restored in live production
- lexical retrieval remains the active grounded backup

## Current runtime truth

- Live MVP: stable
- Gemini provider: degraded by quota, but no longer blocks production usefulness
- OpenRouter provider: currently validated and serving true AI generation
- User-facing experience: functional through AI Mode, cache-backed replay, or fallback academic mode
- Document intelligence: frontend PDF workflow exists and stays honest about retrieval-only vs grounded AI behavior

## Honest limitation

Scholr's external provider is still susceptible to quota and model access variability. The platform mitigates this with provider diagnostics, recovery, caching, and deterministic academic fallback, but that is not the same as unlimited provider capacity.
