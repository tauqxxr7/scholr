# Scholr Production Evidence

## Live endpoints

- Frontend: [https://scholr-coral.vercel.app](https://scholr-coral.vercel.app)
- Backend health: [https://scholr-k9sj.onrender.com/health](https://scholr-k9sj.onrender.com/health)
- Provider health: [https://scholr-k9sj.onrender.com/health/provider](https://scholr-k9sj.onrender.com/health/provider)
- Generation smoke test: [https://scholr-k9sj.onrender.com/health/generate-test](https://scholr-k9sj.onrender.com/health/generate-test)

## Current production evidence table

| Capability | Status | Proof |
| --- | --- | --- |
| Deployment | Live | Vercel frontend + Render backend |
| Mobile responsiveness | Verified | iOS/manual verification and responsive workspace shell |
| SSE streaming | Working | Shared FastAPI SSE routes and client stream parser |
| Provider recovery | Active | Provider diagnostics and background validation loop |
| Fallback mode | Working | No-empty-output guarantee and fallback academic mode |
| Cache behavior | Working | Exact cache, warm cache, optimistic hydration |
| Document intelligence backend | Foundation validated | Upload + answer routes, retrieval-only fallback, citation metadata |
| User validation | Ready | Templates and research pack present, no fabricated data |
| CI status | Live | Backend CI, Frontend CI, Repo Hygiene passing |

## Current runtime truth

- Live MVP: stable
- Gemini provider: can degrade due to quota or project-level model access
- User-facing experience: functional through AI Mode, cache-backed replay, or fallback academic mode
- Document intelligence: backend-first foundation exists; frontend PDF UX is intentionally deferred

## Honest limitation

Scholr's external provider is still susceptible to quota and model access variability. The platform mitigates this with provider diagnostics, recovery, caching, and deterministic academic fallback, but that is not the same as unlimited provider capacity.
