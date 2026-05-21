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
| First token latency | frontend analytics + SSE logs | Measured live | Research `7883 ms`, Notes `6663 ms`, Doubt `6239 ms` from live production checks on 2026-05-21 |
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
| Live document workflow verification | manual live probe + smoke script | Verified with fixture | `academic-sample.pdf` upload and retrieval-only answer succeeded live |

## Real production measurements

### Live AI generation proof

| Route | Topic / Question | Active Provider | First Token Latency | Full Completion Latency | `[DONE]` Integrity | Fallback Used |
| --- | --- | --- | --- | --- | --- | --- |
| Research | `DBMS normalization` | `openrouter` | `7883 ms` | `7904 ms` | Yes | No |
| Notes | `Operating system deadlock` | `openrouter` | `6663 ms` | `6673 ms` | Yes | No |
| Doubt | `What is normalization in DBMS?` | `openrouter` | `6239 ms` | `6390 ms` | Yes | No |

### Live provider health snapshot

- Active provider: `openrouter`
- Selected model: `google/gemini-2.0-flash-lite-001`
- Gemini provider ready: `false`
- OpenRouter provider ready: `true`
- Selected model validation status: `validated`
- Fallback provider: `academic_fallback_engine`

### Live document workflow snapshot

- Upload status: `ready_with_lexical_fallback`
- Answer mode: `retrieval_only`
- Retrieval mode: `lexical`
- Citations: present
- Semantic retrieval ready: not yet live

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
- Semantic document retrieval depends on provider-backed embeddings, so live `/health/documents` should be expected to report lexical default mode while the provider is degraded.
- No production dashboard exists yet for aggregated metrics; current proof comes from endpoints, logs, and manual validation records.
