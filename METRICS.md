# Scholr Metrics

This document tracks measurable production proof without inventing data.

## Live surfaces

- Frontend: [https://scholr-coral.vercel.app](https://scholr-coral.vercel.app)
- Backend health: [https://scholr-k9sj.onrender.com/health](https://scholr-k9sj.onrender.com/health)
- Provider health: [https://scholr-k9sj.onrender.com/health/provider](https://scholr-k9sj.onrender.com/health/provider)
- Generation smoke test: [https://scholr-k9sj.onrender.com/health/generate-test](https://scholr-k9sj.onrender.com/health/generate-test)
- Document health: [https://scholr-k9sj.onrender.com/health/documents](https://scholr-k9sj.onrender.com/health/documents)

## Instrumented runtime metrics

| Metric | Source | Current status | Notes |
| --- | --- | --- | --- |
| First token latency | frontend analytics + SSE logs | Measured live | Research `6967 ms`, Notes `7995 ms`, Doubt `5965 ms` from the refreshed live production proof capture on 2026-05-21 |
| Fallback activation rate | frontend analytics + backend logs | Instrumented | Useful for quota degradation analysis |
| Cache hit rate | backend cache logs | Instrumented | Includes exact cache and warm-cache behavior |
| Provider recovery attempts | `/health/provider` | Instrumented | Background recovery loop exposes attempts |
| Provider recovery success | backend structured logs | Instrumented | Logged when validated provider returns to healthy |
| Requests per minute | `/health` runtime diagnostics | Instrumented | Current MVP quota protection view |
| Quota cooldown remaining | `/health/provider` | Instrumented | Visible while provider is cooling down |
| Last successful generation timestamp | `/health/provider` | Instrumented | Use for outage analysis |
| Upload success rate | frontend analytics + backend upload logs | Instrumented | Do not report percentages until real sessions accumulate |
| Retrieval latency | backend document logs | Instrumented | Upload and answer durations logged separately |
| Document answer latency | frontend analytics + backend logs | Instrumented | Useful for mobile perception and RAG tuning |
| Citation count | document answer payload + analytics | Instrumented | Track whether answers stay grounded |
| Lexical vs semantic retrieval usage | `/health/documents` + document answer payload | Instrumented | Supports semantic upgrade planning |
| Embedding latency | `/health/documents` | Instrumented | Reports the last embedding-provider latency snapshot |
| Vector query latency | `/health/documents` | Instrumented | Reports the last semantic-vector query latency snapshot |
| Vector store health | `/health/documents` | Instrumented | Distinguishes provider degradation from vector-store unavailability |
| Upload failure rate | `/health/documents` + backend logs | Instrumented | Raw counts only until real traffic volume accumulates |
| SSE interruption rate | `/health` runtime diagnostics | Instrumented | Exposed as stream interruption counts, not fabricated percentages |
| Live document workflow verification | manual live probe + smoke script | Verified with fixture | `academic-sample.pdf` upload and grounded lexical answer succeeded live |
| Failure recovery rate | provider diagnostics + live proof capture | Not enough real history yet | Do not calculate a rate until longer-lived production telemetry exists |

## Current MVP Status

- Public-access MVP is stable after the mobile landing responsiveness fix.
- OpenRouter is the active production generation provider in the latest proof loop.
- Semantic retrieval is supported when embedding/vector diagnostics report ready.
- Lexical fallback remains preserved for document answers.
- Auth is postponed until a custom-domain-ready rollout is planned.
- PostgreSQL plus pgvector is the next persistence and retrieval infrastructure milestone.
- Student validation is pending; no student scores, quotes, or retention numbers are reported yet.

## Mobile Speed Targets

Scholr now follows a fast-first response contract for mobile reliability.

| Metric | Target | Behavior |
| --- | --- | --- |
| First token latency | <= 5 seconds | If no token starts in time, backend falls back or returns a specific timeout category. |
| Total completion latency | 8 to 12 seconds target, 20 seconds hard cutoff | Fast mode keeps answers compact and avoids long provider completions. |
| Second-request latency | Same class as first request | Provider validation is cached; OpenRouter streams tokens instead of waiting for full completion. |
| Output length | Fast: about 350 to 550 words max depending on module | Deep mode is optional and explicitly selected by the user. |
| Partial-output recovery | Always preserve partial tokens | If a stream fails after tokens arrive, UI shows `Answer completed partially. Tap retry for deeper version.` |
| Frontend stream parse latency | Instrumented per generation | Client records stream parsing latency without blocking rendering. |
| Provider latency | Exposed through provider diagnostics/logs | Provider runtime cutoff is tuned for mobile responsiveness. |

## Public MVP verification checklist

| Surface / System | Measurement Type | Latest Evidence | Status |
| --- | --- | --- | --- |
| Landing page | Route + responsive viewport check | Vercel live route, iPhone/Android/tablet emulation | Passed |
| Dashboard | Route check | Public `/dashboard` route | Passed |
| Research | SSE stream integrity | first token, completion, `[DONE]`, mode metadata | Passed |
| Notes | SSE stream integrity | first token, completion, `[DONE]`, mode metadata | Passed |
| Doubt | SSE stream integrity | first token, completion, `[DONE]`, mode metadata | Passed |
| Documents | Upload + answer smoke | fixture PDF, citation payload | Passed |
| Mobile | Viewport behavior | no horizontal overflow in emulated mobile widths | Passed by emulation |
| Desktop | Route/layout sanity | live desktop route check | Passed |
| Provider health | Diagnostics endpoint | `/health/provider` | Passed |
| Semantic retrieval | Document diagnostics | `/health/documents` semantic flags and retrieval mode | Supported |
| Lexical retrieval | Fallback capability | document answer fallback path | Preserved |
| SSE streaming | Stream parser behavior | `[DONE]` received for AI modules | Passed |

## Real production measurements

### Live AI generation proof

| Route | Topic / Question | Active Provider | First Token Latency | Full Completion Latency | `[DONE]` Integrity | Fallback Used |
| --- | --- | --- | --- | --- | --- | --- |
| Research | `DBMS normalization` | `openrouter` | `6967 ms` | `7198 ms` | Yes | No |
| Notes | `Operating system deadlock` | `openrouter` | `7995 ms` | `8015 ms` | Yes | No |
| Doubt | `What is normalization in DBMS?` | `openrouter` | `5965 ms` | `6225 ms` | Yes | No |

### Live response lengths

- Research response length: `4437`
- Notes response length: `5187`
- Doubt response length: `3291`
- Generate-test latency: `543 ms`

### Live provider health snapshot

- Active provider: `openrouter`
- Selected model: `google/gemini-2.0-flash-lite-001`
- Gemini provider ready: `false`
- OpenRouter provider ready: `true`
- Selected model validation status: `validated`
- Fallback provider: `academic_fallback_engine`

### Live document workflow snapshot

- Upload status: `ready`
- Answer mode: `grounded_generation`
- Retrieval mode: `semantic`
- Citations: present
- Semantic retrieval ready: live
- Embedding provider: `openrouter`
- Embedding model: `openai/text-embedding-3-small`
- Embedding latency: `1035 ms`
- Vector store health: `ready`

## Visual production proof

- Desktop home screenshot: [docs/proof/desktop-home-live.png](docs/proof/desktop-home-live.png)
- Desktop research screenshot: [docs/proof/desktop-research-live.png](docs/proof/desktop-research-live.png)
- Mobile notes screenshot: [docs/proof/mobile-notes-live.png](docs/proof/mobile-notes-live.png)
- Mobile documents screenshot: [docs/proof/mobile-documents-live.png](docs/proof/mobile-documents-live.png)
- Live stream proof panel: [docs/proof/live-stream-proof.png](docs/proof/live-stream-proof.png)
- Provider proof panel: [docs/proof/provider-proof.png](docs/proof/provider-proof.png)
- Document proof panel: [docs/proof/document-proof.png](docs/proof/document-proof.png)

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
- Semantic document retrieval still depends on a validated embedding provider, so live `/health/documents` may continue to report lexical default mode even while generation is healthy through OpenRouter.
- No production dashboard exists yet for aggregated metrics; current proof comes from endpoints, logs, and manual validation records.
- Physical-device iPhone retesting for the latest landing-page fix has not been newly recorded in this pass; use the validation checklist before claiming it.
