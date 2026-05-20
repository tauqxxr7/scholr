# Scholr Metrics

This document tracks measurable production proof without inventing data.

## Live surfaces

- Frontend: [https://scholr-coral.vercel.app](https://scholr-coral.vercel.app)
- Backend health: [https://scholr-k9sj.onrender.com/health](https://scholr-k9sj.onrender.com/health)
- Provider health: [https://scholr-k9sj.onrender.com/health/provider](https://scholr-k9sj.onrender.com/health/provider)
- Generation smoke test: [https://scholr-k9sj.onrender.com/health/generate-test](https://scholr-k9sj.onrender.com/health/generate-test)

## Instrumented runtime metrics

| Metric | Source | Current status | Notes |
| --- | --- | --- | --- |
| First token latency | frontend analytics + SSE logs | Instrumented | Collect real values after validation traffic |
| Fallback activation rate | frontend analytics + backend logs | Instrumented | Useful for quota degradation analysis |
| Cache hit rate | backend cache logs | Instrumented | Includes exact cache and warm-cache behavior |
| Provider recovery attempts | `/health/provider` | Instrumented | Background recovery loop exposes attempts |
| Provider recovery success | backend structured logs | Instrumented | Logged when validated provider returns to healthy |
| Requests per minute | `/health` runtime diagnostics | Instrumented | Current MVP quota protection view |
| Quota cooldown remaining | `/health/provider` | Instrumented | Visible while provider is cooling down |
| Last successful generation timestamp | `/health/provider` | Instrumented | Use for outage analysis |

## Product metrics to collect

- student sessions per day
- module opens per day
- generation started count
- generation completed count
- generation failed count
- repeat usage within 7 days
- usefulness rating average from real students

## Validation goals

- 10 to 15 BTech students test the live product
- at least 5 return for a second session
- at least 3 use more than one module
- at least 2 explicitly say it saves time
- at least 1 says they would pay or strongly want it kept

## Known limitations

- Gemini quota and project-level model access can still move Scholr into resilience-backed fallback mode.
- No production dashboard exists yet for aggregated metrics; current proof comes from endpoints, logs, and manual validation records.
