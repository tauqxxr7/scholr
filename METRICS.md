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
| First token latency | frontend analytics + SSE logs | Measured live | Research `7752 ms`, Notes `8666 ms`, Doubt `4729 ms` from live production proof capture on 2026-05-21 |
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

## Real production measurements

### Live AI generation proof

| Route | Topic / Question | Active Provider | First Token Latency | Full Completion Latency | `[DONE]` Integrity | Fallback Used |
| --- | --- | --- | --- | --- | --- | --- |
| Research | `DBMS normalization` | `openrouter` | `7752 ms` | `7970 ms` | Yes | No |
| Notes | `Operating system deadlock` | `openrouter` | `8666 ms` | `8890 ms` | Yes | No |
| Doubt | `What is normalization in DBMS?` | `openrouter` | `4729 ms` | `4746 ms` | Yes | No |

### Live response lengths

- Research response length: `5557`
- Notes response length: `5980`
- Doubt response length: `3040`
- Generate-test latency: `579 ms`

### Live provider health snapshot

- Active provider: `openrouter`
- Selected model: `google/gemini-2.0-flash-lite-001`
- Gemini provider ready: `false`
- OpenRouter provider ready: `true`
- Selected model validation status: `validated`
- Fallback provider: `academic_fallback_engine`

### Live document workflow snapshot

- Upload status: `ready_with_lexical_fallback`
- Answer mode: `grounded_generation`
- Retrieval mode: `lexical`
- Citations: present
- Semantic retrieval ready: not yet live
- Embedding provider ready: false in the latest honest live document-health check
- Vector store health: reported separately from provider health through `/health/documents`

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
