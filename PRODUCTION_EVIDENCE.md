# Scholr Production Evidence

## Live endpoints

- Frontend: [https://scholr-coral.vercel.app](https://scholr-coral.vercel.app)
- Backend: [https://scholr-k9sj.onrender.com/health](https://scholr-k9sj.onrender.com/health)
- Provider health: [https://scholr-k9sj.onrender.com/health/provider](https://scholr-k9sj.onrender.com/health/provider)
- Generation smoke test: [https://scholr-k9sj.onrender.com/health/generate-test](https://scholr-k9sj.onrender.com/health/generate-test)

## Current production evidence table

| Capability | Status | Proof |
| --- | --- | --- |
| Deployment | Live | Vercel frontend + Render backend |
| Mobile responsiveness | Verified | iOS/manual verification and responsive workspace shell |
| SSE streaming | Working | shared FastAPI SSE routes and client stream parser |
| Provider recovery | Active | provider diagnostics and background validation loop |
| Fallback mode | Working | no-empty-output guarantee and fallback academic mode |
| Cache behavior | Working | exact cache, warm cache, optimistic hydration |
| User validation | In progress | templates ready, no fabricated data |

## Current runtime truth

- Live MVP: stable
- Gemini provider: degraded due to quota/model access
- User-facing experience: functional through fallback academic mode and cache-backed responses

## Honest limitation

Scholr’s external provider is still susceptible to quota and model access variability. The platform mitigates this with provider diagnostics, recovery, caching, and deterministic academic fallback, but that is not the same as unlimited provider capacity.
