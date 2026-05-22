# Scholr Public MVP Verification Checklist

Use this checklist after production deploys and before claiming the MVP is stable.

Do not mark physical-device checks as passed unless they were actually performed on that device.

## Deployment

| Check | Expected Result | Status | Evidence / Notes |
| --- | --- | --- | --- |
| Vercel production deployment | Latest commit is deployed and ready | TBD | TBD |
| Render backend | `/health` returns 200 | TBD | TBD |
| Frontend CI | GitHub Actions success | TBD | TBD |
| Repo Hygiene | GitHub Actions success | TBD | TBD |

## Public Routes

| Route | Expected Result | Status | Evidence / Notes |
| --- | --- | --- | --- |
| `/` | landing page loads, no horizontal overflow | TBD | TBD |
| `/dashboard` | public dashboard opens without sign-in | TBD | TBD |
| `/research` | Research workspace loads | TBD | TBD |
| `/notes` | Notes workspace loads | TBD | TBD |
| `/doubt` | Doubt workspace loads | TBD | TBD |
| `/documents` | Document workspace loads | TBD | TBD |

## AI And Streaming

| Flow | Expected Result | Status | Evidence / Notes |
| --- | --- | --- | --- |
| Research generation | streamed output, mode badge, `[DONE]` | TBD | TBD |
| Notes generation | streamed output, mode badge, `[DONE]` | TBD | TBD |
| Doubt generation | streamed output, mode badge, `[DONE]` | TBD | TBD |
| Retry button | reruns same request | TBD | TBD |
| Fallback mode | useful academic output if provider degrades | TBD | TBD |
| No-empty-output guarantee | no blank result panel after submit | TBD | TBD |

## Provider Health

| Endpoint | Expected Result | Status | Evidence / Notes |
| --- | --- | --- | --- |
| `/health/provider` | provider status, active provider, selected model | TBD | TBD |
| `/health/generate-test` | tiny generation smoke result | TBD | TBD |
| OpenRouter path | active when Gemini is degraded | TBD | TBD |
| Gemini path | primary provider remains configured when quota/model access allows | TBD | TBD |

## Documents And Retrieval

| Flow | Expected Result | Status | Evidence / Notes |
| --- | --- | --- | --- |
| `/health/documents` | retrieval health and embedding diagnostics | TBD | TBD |
| PDF upload | valid PDF uploads and reaches ready state | TBD | TBD |
| Document answer | answer includes citations/snippets | TBD | TBD |
| Semantic retrieval | marked ready only when embedding/vector path is healthy | TBD | TBD |
| Lexical fallback | still works if semantic path is unavailable | TBD | TBD |
| Citation rendering | document name, page/chunk, snippet visible | TBD | TBD |

## Device Coverage

| Device / Viewport | Expected Result | Status | Evidence / Notes |
| --- | --- | --- | --- |
| iPhone SE viewport | no over-zoomed landing layout | TBD | viewport emulation is acceptable if marked as such |
| iPhone 13/14 viewport | no over-zoomed landing layout | TBD | viewport emulation is acceptable if marked as such |
| Android standard viewport | no overflow or oversized cards | TBD | TBD |
| Tablet viewport | balanced spacing and readable hierarchy | TBD | TBD |
| Desktop | preserved hero, cards, dashboard, and workspace layout | TBD | TBD |
| Physical iPhone Safari | only mark passed if tested on real device | TBD | TBD |

## Regression Guardrails

| Area | Must Not Regress | Status | Evidence / Notes |
| --- | --- | --- | --- |
| Public access | no auth wall or Clerk dependency | TBD | TBD |
| SSE parser | handles partial chunks and `[DONE]` | TBD | TBD |
| Rate limiting | specific messages, no generic failures | TBD | TBD |
| Document upload | file validation and temp cleanup remain safe | TBD | TBD |
| Secrets hygiene | no `.env`, keys, db, venv, node_modules, `.next` tracked | TBD | TBD |
