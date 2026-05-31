# Scholr Engineering Sprint Commit Summary

Date: 2026-05-24

## Tasks Completed

### Task 1 - History persistence fix

- Commit: `c750b21`
- Message: `fix: use persistent disk path for SQLite to survive Render deploys`
- Files changed:
  - `DEPLOYMENT.md`
  - `backend/.env.example`
  - `backend/db/database.py`

### Task 2 - Research Fast/Deep toggle

- Commit: `07f7230`
- Message: `feat: add Fast/Deep mode toggle to Research module matching Notes and Doubt`
- Files changed:
  - `backend/agents/research_agent.py`
  - `backend/models/schemas.py`
  - `backend/routers/research.py`
  - `frontend/components/ai/ai-module-page.tsx`

### Task 3 - Documents cold-load skeleton

- Commit: `ce00d75`
- Message: `fix: show loading skeleton on Documents health check instead of immediate Unavailable text`
- Files changed:
  - `frontend/components/documents/document-workspace.tsx`

### Task 4 - PostHog analytics

- Commit: `7d21c80`
- Message: `feat: add PostHog analytics with module-level event tracking`
- Files changed:
  - `frontend/app/layout.tsx`
  - `frontend/components/PostHogProvider.tsx`
  - `frontend/components/ai/ai-module-page.tsx`
  - `frontend/components/documents/document-workspace.tsx`
  - `frontend/lib/analytics.ts`
  - `frontend/lib/posthog.ts`
  - `frontend/package-lock.json`
  - `frontend/package.json`

### Task 5 - Sentry backend monitoring

- Commit: `b74c128`
- Message: `feat: add Sentry error monitoring to FastAPI backend`
- Files changed:
  - `backend/.env.example`
  - `backend/main.py`
  - `backend/requirements.txt`

### Task 6 - Thumbs up/down feedback

- Commit: `4598560`
- Message: `feat: add thumbs up/down feedback signal on all AI responses`
- Files changed:
  - `backend/db/crud.py`
  - `backend/db/database.py`
  - `backend/main.py`
  - `backend/models/schemas.py`
  - `backend/routers/feedback.py`
  - `frontend/components/ai/ResponseFeedback.tsx`
  - `frontend/components/ai/ai-module-page.tsx`
  - `frontend/lib/analytics.ts`
  - `frontend/lib/api.ts`

### Task 7 - Structured response time logging

- Commit: `932d1cb`
- Message: `feat: add structured response time logging to all streaming endpoints`
- Files changed:
  - `backend/routers/_streaming.py`
  - `backend/routers/doubt.py`
  - `backend/routers/notes.py`
  - `backend/routers/research.py`

### Task 8 - Backend unit tests

- Commit: `24c5a78`
- Message: `feat: add backend unit tests for agents and routers with CI integration`
- Files changed:
  - `.github/workflows/backend-ci.yml`
  - `backend/agents/doubt_agent.py`
  - `backend/agents/notes_agent.py`
  - `backend/requirements.txt`
  - `backend/tests/__init__.py`
  - `backend/tests/conftest.py`
  - `backend/tests/test_agents.py`
  - `backend/tests/test_routers.py`

### Task 9 - Retry button

- Commit: `44edf46`
- Message: `feat: add retry button on failed or partial AI responses`
- Files changed:
  - `frontend/components/ai/ai-module-page.tsx`

## Test Results

- `python -m pytest backend/tests/ -v`: passed, 12 tests.
- `python -m compileall backend`: passed.
- Backend import check with local `SQLITE_PATH`: passed.
- `npm run lint`: passed.
- `npx tsc --noEmit`: passed.
- `npm run build`: passed.
- Local built frontend routes returning 200:
  - `/`
  - `/research`
  - `/notes`
  - `/doubt`
  - `/documents`
  - `/dashboard`

## UI Verification

- Fast/Deep toggle is present through the shared AI module page used by Research, Notes, and Doubt.
- Research sends both `mode` and `response_mode` for compatibility.
- Documents health indicators show `Checking system status...` and pulse skeletons before resolved health data.

## CI Notes

- Backend CI now installs dependencies, compiles the backend, runs `python -m pytest tests/ -v`, imports the app, and performs a route smoke check.
- Frontend CI-equivalent local checks passed with lint, TypeScript, and production build.
- Remote GitHub Actions and Vercel deployment are verified after the final summary commit is pushed.

# Sprint 2 Verification Addendum

Date: 2026-05-24

## Sprint 2 Task Status

### Task 1 - Clerk authentication

- Status: Not implemented in this visible request.
- Commit: none in this Sprint 2 pass.
- Verification result: `/sign-in` and `/sign-up` returned 404 in the built local frontend.
- Note: Active Clerk authentication was previously removed to restore stable public MVP access.

### Task 2 - PostgreSQL migration

- Status: Not implemented in this visible request.
- Commit: none in this Sprint 2 pass.
- Verification result: existing backend remains SQLite with PostgreSQL-ready `DATABASE_URL` support.

### Task 3 - Landing page conversion

- Status: Not implemented in this visible request.
- Commit: none in this Sprint 2 pass.

### Task 4 - First-time onboarding

- Status: Not implemented in this visible request.
- Commit: none in this Sprint 2 pass.

### Task 5 - Keyboard shortcuts

- Status: Not implemented in this visible request.
- Commit: none in this Sprint 2 pass.

### Task 6 - PDF export

- Status: Not implemented in this visible request.
- Commit: none in this Sprint 2 pass.

### Task 7 - SEO sitemap + robots

- Status: Not implemented in this visible request.
- Commit: none in this Sprint 2 pass.

### Task 8 - Metrics and waitlist endpoints

- Status: Not implemented in this visible request.
- Commit: none in this Sprint 2 pass.
- Verification result: `/api/metrics` and `/api/waitlist` returned 404 via FastAPI TestClient.

### Task 9 - README update

- Status: completed.
- Commit: `0c406d7`
- Message: `docs: update README with quick demo, architecture diagram, and local setup guide`
- Files changed:
  - `README.md`

### Task 10 - Final verification

- Status: completed with documented route gaps.
- Commit: this commit.
- Message: `chore: sprint 2 final verification and commit summary update`
- Files changed:
  - `COMMIT_SUMMARY.md`

## Sprint 2 Test Results

- `python -m pytest backend/tests/ -v`: passed, 12 tests.
- `python -m compileall backend`: passed.
- `npm run lint`: passed.
- `npx tsc --noEmit`: passed.
- `npm run build`: passed.
- Built frontend routes returning 200:
  - `/`
  - `/research`
  - `/notes`
  - `/doubt`
  - `/documents`
  - `/dashboard`
- Built frontend routes missing:
  - `/sign-in`
  - `/sign-up`
- Backend API routes missing:
  - `/api/metrics`
  - `/api/waitlist`
- Sprint 2 separate commits visible in this pass: 1 implementation commit plus this verification commit.

# Sprint 2 Retry

Date: 2026-05-24

## Task Results

### Task 1 - SEO sitemap + robots

- Status: completed.
- Commit: `d9ad944`
- Message: `feat: add sitemap.xml and robots.txt for SEO`
- Files changed:
  - `frontend/app/sitemap.ts`
  - `frontend/app/robots.ts`

### Task 2 - `/api/metrics` endpoint

- Status: completed.
- Commit: `69bb95f`
- Message: `feat: add /api/metrics endpoint for aggregate usage and feedback stats`
- Files changed:
  - `backend/routers/metrics.py`
  - `backend/main.py`
  - `backend/tests/test_routers.py`

### Task 3 - Waitlist endpoint + landing form

- Status: completed.
- Commit: `cd1405f`
- Message: `feat: add email waitlist with backend endpoint and landing page capture form`
- Files changed:
  - `backend/db/database.py`
  - `backend/routers/waitlist.py`
  - `backend/main.py`
  - `backend/requirements.txt`
  - `backend/tests/test_routers.py`
  - `frontend/app/page.tsx`

### Task 4 - Landing page CTA improvements

- Status: completed.
- Commit: `829bca6`
- Message: `feat: improve landing page CTA copy and add how-it-works section`
- Files changed:
  - `frontend/app/page.tsx`

### Task 5 - First-time onboarding

- Status: completed.
- Commit: `64e7aeb`
- Message: `feat: add first-time user onboarding cards on empty dashboard`
- Files changed:
  - `frontend/app/(dashboard)/dashboard/page.tsx`
  - `frontend/components/ai/ai-module-page.tsx`

### Task 6 - Keyboard shortcuts hook

- Status: completed.
- Commit: `97f27f5`
- Message: `feat: add useKeyboardShortcuts hook standardised across all modules`
- Files changed:
  - `frontend/hooks/useKeyboardShortcuts.ts`
  - `frontend/components/ai/ai-module-page.tsx`

### Task 7 - PDF export

- Status: completed.
- Commit: `6700601`
- Message: `feat: add PDF export of AI responses with Scholr branding`
- Files changed:
  - `frontend/package.json`
  - `frontend/package-lock.json`
  - `frontend/lib/exportPdf.ts`
  - `frontend/components/ai/ai-module-page.tsx`

### Task 8 - PostgreSQL engine upgrade

- Status: completed.
- Commit: `9f57def`
- Message: `feat: PostgreSQL-ready engine with connection pooling and postgres:// URL rewrite`
- Files changed:
  - `backend/db/database.py`
  - `backend/tests/test_routers.py`
  - `DEPLOYMENT.md`

### Final verification

- Status: completed.
- Commit: this commit.
- Message: `chore: sprint 2 retry â€” final verification and commit summary`
- Files changed:
  - `COMMIT_SUMMARY.md`

## Sprint 2 Retry Verification

- `python -m pytest backend/tests/ -v`: passed, 16 tests.
- `python -m compileall backend`: passed.
- `npm run lint`: passed.
- `npx tsc --noEmit`: passed.
- `npm run build`: passed.
- Built frontend routes returning 200:
  - `/`
  - `/research`
  - `/notes`
  - `/doubt`
  - `/documents`
  - `/dashboard`
- `GET /api/metrics`: passed, returned `searches` and `feedback`.
- `POST /api/waitlist`: passed with valid email.
- `git log --oneline -10`: shows all 8 Sprint 2 retry implementation commits.

# Sprint 3

Date: 2026-05-24

## Task Results

### Bug Fix A - Landing page CTA

- Status: completed.
- Commit: `cdf831f`
- Message: `fix: update landing page CTA and subheading text to student-facing copy`
- Files changed:
  - `frontend/app/page.tsx`

### Bug Fix B - Dashboard onboarding

- Status: completed.
- Commit: `094fe2e`
- Message: `fix: repair dashboard onboarding hydration - show cards for new users with empty history`
- Files changed:
  - `frontend/app/(dashboard)/dashboard/page.tsx`

### Task 1 - Clerk auth scaffold

- Status: completed.
- Commit: `a5f0002`
- Message: `feat: add Clerk auth scaffold with optional JWT user tagging on history`
- Files changed:
  - `frontend/package.json`
  - `frontend/package-lock.json`
  - `frontend/middleware.ts`
  - `frontend/app/layout.tsx`
  - `frontend/app/(dashboard)/layout.tsx`
  - `frontend/app/sign-in/[[...sign-in]]/page.tsx`
  - `frontend/app/sign-up/[[...sign-up]]/page.tsx`
  - `frontend/.env.example`
  - `backend/auth/__init__.py`
  - `backend/auth/clerk.py`
  - `backend/requirements.txt`
  - `backend/db/database.py`
  - `backend/db/crud.py`
  - `backend/routers/research.py`
  - `backend/routers/notes.py`
  - `backend/routers/doubt.py`
  - `backend/routers/history.py`

### Task 2 - AI output quality

- Status: completed.
- Commit: `9763255`
- Message: `feat: strengthen AI prompt structure enforcement and add output section validation logging`
- Files changed:
  - `backend/agents/_validation.py`
  - `backend/agents/research_agent.py`
  - `backend/agents/notes_agent.py`
  - `backend/agents/doubt_agent.py`
  - `backend/routers/_streaming.py`
  - `backend/routers/research.py`
  - `backend/routers/notes.py`
  - `backend/routers/doubt.py`

### Task 3 - Response caching

- Status: completed.
- Commit: `638a80e`
- Message: `feat: add in-memory response cache with TTL and LRU eviction for repeated queries`
- Files changed:
  - `backend/cache/__init__.py`
  - `backend/cache/response_cache.py`
  - `backend/routers/_streaming.py`
  - `backend/routers/research.py`
  - `backend/routers/notes.py`
  - `backend/routers/doubt.py`
  - `backend/routers/metrics.py`
  - `backend/tests/test_routers.py`

### Task 4 - Rate limiting upgrade

- Status: completed.
- Commit: `dd64a3e`
- Message: `feat: upgrade rate limiting with slowapi per-IP tracking on all endpoints`
- Files changed:
  - `backend/core/slowapi_limiter.py`
  - `backend/requirements.txt`
  - `backend/main.py`
  - `backend/routers/research.py`
  - `backend/routers/notes.py`
  - `backend/routers/doubt.py`
  - `backend/routers/waitlist.py`
  - `backend/routers/metrics.py`

### Task 5 - GitHub social proof

- Status: completed.
- Commit: `23d7eef`
- Message: `docs: improve README header with live link and star CTA, update og metadata`
- Files changed:
  - `README.md`
  - `frontend/app/layout.tsx`

### Task 6 - Pre-launch safety

- Status: completed.
- Commit: `65d2068`
- Message: `feat: add privacy page, disclaimer banner, pre-launch user safety improvements`
- Files changed:
  - `frontend/components/DisclaimerBanner.tsx`
  - `frontend/app/(dashboard)/layout.tsx`
  - `frontend/app/privacy/page.tsx`

### Final verification

- Status: completed.
- Commit: this commit.
- Message: `chore: sprint 3 final verification and summary`
- Files changed:
  - `COMMIT_SUMMARY.md`

## Sprint 3 Verification

- `python -m pytest backend/tests/ -v`: passed, 19 tests.
- `python -m compileall backend`: passed.
- `npm run lint`: passed.
- `npx tsc --noEmit`: passed.
- `npm run build`: passed with Next.js middleware deprecation warning only.
- Built frontend routes include `/`, `/research`, `/notes`, `/doubt`, `/documents`, `/dashboard`, `/sign-in`, `/sign-up`, `/sitemap.xml`, and `/robots.txt`.
- `/api/metrics` now includes `cache` and `rate_limits`.
- Rate limiting remains layered with existing Scholr runtime quota checks.

# Sprint 4

Date: 2026-05-25

## Task Results

- Issue Fix 1 - Landing CTA final: completed. Commit `2281619`. Verified source replacements line-by-line and fixed CTA encoding to `Try Scholr free — no signup needed`.
- Issue Fix 2 - Render rebuild force: completed. Commit `6bd9b89`. Confirmed `metrics` and `waitlist` routers are imported/included and bumped backend health version to `1.4.0`.
- Task 1 - `/health/routes` endpoint: completed. Commit `f5d3070`. Added registered-route diagnostics and tests for `/api/metrics`, `/api/waitlist`, and `/api/research`.
- Task 2 - Render deploy CI check: completed. Commit `f37e6c2`. Added non-blocking `verify-deployment` job after backend CI.
- Task 3 - Validation tracking: completed. Commit `8da72c9`. Added validation session/summary endpoints and silent dashboard session tracking.
- Task 4 - Evidence endpoint: completed. Commit `ba5862a`. Added `/api/evidence` Microsoft for Startups technical proof package and test coverage.
- Task 5 - LinkedIn post data: completed. Commit `98b2d24`. Added `/api/linkedin/post-data` with live-count post templates.
- Task 6 - Docs folder cleanup: completed. Commit `61f3989`. Moved root docs into `/docs` with `git mv` and updated README links.
- Task 7 - Topics SEO page: completed. Commit `d9edc90`. Added `/topics`, sitemap entry, and footer link.
- Final verification: completed. Commit: this commit. Message: `chore: sprint 4 final verification and commit summary`.

## Sprint 4 Verification

- `python -m pytest backend/tests/ -v`: passed, 23 tests.
- `python -m compileall backend`: passed.
- `npm run lint`: passed.
- `npx tsc --noEmit`: passed.
- `npm run build`: passed with Next.js middleware deprecation warning only.
- Verified backend source includes `/health/routes`, `/api/metrics`, `/api/waitlist`, `/api/evidence`, `/api/validation/session`, `/api/validation/summary`, and `/api/linkedin/post-data` through router registration.
- Root markdown files now limited to `README.md`, `DEPLOYMENT.md`, `METRICS.md`, and `COMMIT_SUMMARY.md`.

# Sprint 5

Date: 2026-05-25

## Task Results

- Issue Fix - render.yaml autoDeploy: completed. Commit `da90184`. Enabled Render `autoDeploy`, pinned `branch: main`, added `/health` health check, and bumped backend version to `1.5.0`.
- Task 1 - Clerk hardening: completed. Commit `d344722`. Clerk now protects dashboard/module routes only when keys are configured and preserves public access without keys.
- Task 2 - Semantic search backend: completed. Commit `176b85c`. Added lazy sentence-transformers embeddings, optional history embeddings, `/api/search`, and deployment note for first-load model latency.
- Task 3 - Search UI dashboard: completed. Commit `a211f35`. Added debounced dashboard history search with similarity scores.
- Task 4 - Abuse prevention: completed. Commit `5d3d26a`. Added input sanitisation, spam-topic SSE response, and waitlist honeypot blocking.
- Task 5 - CSV export: completed. Commit `bacbb41`. Added `/api/history/export`, dashboard CSV link, and test coverage.
- Final verification: completed. Commit: this commit. Message: `chore: sprint 5 final verification and summary`.

## Sprint 5 Verification

- `python -m pytest backend/tests/ -v`: passed, 28 tests.
- `python -m compileall backend`: passed.
- `npm run lint`: passed.
- `npx tsc --noEmit`: passed.
- `npm run build`: passed with Next.js middleware deprecation warning only.
- Verified backend source includes `/health/routes`, `metrics`, `waitlist`, `evidence`, `validation`, `linkedin`, `search`, and `history` router registration.
- `git log --oneline -15` shows all Sprint 5 implementation commits on the current branch.

# Sprint 6

Date: 2026-05-25

## Task Results

- Issue Fix - render.yaml + smoke test: completed. Commit `413373a`. Verified `autoDeploy: true`, `branch: main`, and `/health` health check; added executable `scripts/smoke-test.sh`.
- Task 1 - Outreach page: completed. Commit `1d9416c`. Added private `/outreach` validation message generator.
- Task 2 - Research topic chips: completed. Commit `cb06210`. Added clickable Research prompt suggestions.
- Task 3 - Notes subject chips: completed. Commit `5639b95`. Added subject quick-select chips for Notes.
- Task 4 - Dashboard stats: completed. Commit `38ccd48`. Added subtle dashboard usage stats from `/api/metrics`.
- Task 5 - Status endpoint + page: completed. Commit `ba293d9`. Added `/api/status`, `/status`, sitemap entry, footer link, and test coverage.
- Task 6 - README recruiter pass: completed. Commit `23a210b`. Added metrics table, topic tags, and Microsoft for Startups context.
- Final verification: completed. Commit: this commit. Message: `chore: sprint 6 final verification and summary`.

## Sprint 6 Verification

- `python -m pytest backend/tests/ -v`: passed, 29 tests.
- `python -m compileall backend`: passed.
- `npm run lint`: passed.
- `npx tsc --noEmit`: passed.
- `npm run build`: passed with Next.js middleware deprecation warning only.
- Verified backend router registration for status, search, history, metrics, waitlist, evidence, validation, linkedin, and feedback.
- Verified frontend build routes include `/research`, `/notes`, `/doubt`, `/documents`, `/dashboard`, `/topics`, `/status`, and `/outreach`.
- `git log --oneline -15` shows all Sprint 6 commits on current head.

# Sprint 7

Date: 2026-05-25

## Task Results

- Issue Fix - duplicate hero subheading: completed. Commit `4d1fdc9`. Removed the duplicate pre-H1 student-facing subheading and updated hero pills to `No signup needed` and `Results in 60 seconds`.
- Task 1 - Share button dashboard: completed. Commit `af5561d`. Added dashboard Web Share API sharing with clipboard fallback.
- Task 2 - Share button response toolbar: completed. Commit `c0665f4`. Added response sharing to the shared AI module toolbar.
- Task 3 - `/demo` page: completed. Commit `1846462`. Added curated demo scenarios and sitemap entry.
- Task 4 - URL param auto-submit: completed. Commit `c611dde`. Research, Notes, and Doubt now prefill and auto-submit valid URL params.
- Task 5 - `/feedback` page: completed. Commit `1e8f1dd`. Added public feedback form, `/api/feedback-form`, footer/sitemap links, and backend test coverage.
- Task 6 - Microsoft application doc: completed. Commit `e194ad1`. Added Microsoft for Startups application support document.
- Final verification: completed. Commit: this commit. Message: `chore: sprint 7 final verification and summary`.

## Sprint 7 Verification

- `python -m pytest backend/tests/ -v`: passed, 30 tests.
- `python -m compileall backend`: passed.
- `npm run lint`: passed.
- `npx tsc --noEmit`: passed.
- `npm run build`: passed with Next.js middleware deprecation warning only.
- Verified frontend build routes include `/research`, `/notes`, `/doubt`, `/documents`, `/dashboard`, `/topics`, `/status`, `/outreach`, `/demo`, and `/feedback`.
- Verified backend source imports and includes the `feedback_form` router.
- `git log --oneline -15` shows all Sprint 7 commits on current head.

# Sprint 8

Date: 2026-05-25

## Task Results

- Issue Fix A - duplicate hero text: completed. Commit `c00402f`. Verified line-by-line that only one hero subheading remains and conversion pills are correct.
- Issue Fix B - generate-test endpoint: completed. Commit `8db9f59`; follow-up `0d1bbf6` ensures the provider stream completes so success telemetry can increment.
- Task 1 - backend status indicator: completed. Commit `878c43b`. Added module-page backend health check and cold-start warning banner.
- Task 2 - Try an example button: completed. Commit `382b0e9`. Added one-click examples for Research, Notes, and Doubt.
- Task 3 - better error messages: completed. Commit `01bc1c2`. Replaced generic failure copy with network, partial-stream, and empty-response recovery guidance.
- Task 4 - GitHub discoverability: completed. Commit `28e7533`. Updated README topics, student audience section, and search-friendly description.
- Task 5 - `/changelog` page: completed. Commit `2d11f15`. Added changelog route, sitemap entry, and footer link.
- Task 6 - startup logging + dynamic version: completed. Commit `4c90da6`. Added startup diagnostics and `APP_VERSION`-driven API versioning.
- Final verification: completed. Commit: this commit. Message: `chore: sprint 8 final verification and summary`.

## Sprint 8 Verification

- `python -m pytest backend/tests/ -v`: passed, 31 tests.
- `python -m compileall backend`: passed.
- `npm run lint`: passed.
- `npx tsc --noEmit`: passed.
- `npm run build`: passed with Next.js middleware deprecation warning only.
- Verified frontend build routes include `/research`, `/notes`, `/doubt`, `/demo`, `/feedback`, `/changelog`, `/status`, and `/topics`.
- Live `/health/generate-test` returned `ai_working: true` with generated text after deployment.
- `git log --oneline -10` shows all Sprint 8 commits on current head.

# Sprint 9

Date: 2026-05-31

## Task Results

- Task 1 - Promise section fix: completed. Commit `bbf83bd`. Replaced internal product strategy language with student-benefit copy.
- Task 2 - Testimonial section: completed. Commit `ce999f1`. Added subtle testimonial placeholders with TODO for real validation quotes.
- Task 3 - Topics page SEO: completed. Commit `eca5a01`. Added generated metadata, popular topic cards, and accurate topic count.
- Task 4 - Loading skeletons: completed. Commit `82d9e9b`. Added reusable skeleton card plus dashboard/status loading states.
- Task 5 - 404 page: completed. Commit `081c597`. Added custom 404 navigation back to Research, Notes, and Home.
- Task 6 - `/ping` endpoint: completed. Commit `6dfafbc`. Added uptime-monitor endpoint, smoke-test coverage, docs note, and backend test.
- Task 7 - Version bump: completed. Commit: this commit. Message: `chore: bump version to 1.6.0 and update commit summary`.

## Sprint 9 Verification So Far

- `python -m pytest backend/tests/ -v`: passed, 35 tests after `/ping`.
- `python -m compileall backend`: passed after `/ping`.
- `npm run lint`: passed for frontend polish tasks.
- `npx tsc --noEmit`: passed for frontend polish tasks.

## Sprint 9 Final Verification

- Final status: completed. Commit: this commit. Message: `chore: sprint 9 final verification`.
- `python -m pytest backend/tests/ -v`: passed, 35 tests.
- `python -m compileall backend`: passed.
- `npm run lint`: passed.
- `npx tsc --noEmit`: passed.
- `npm run build`: passed with Next.js middleware deprecation warning only.
- Frontend routes verified in source/build: `/research`, `/notes`, `/doubt`, `/dashboard`, `/topics`, `/status`, `/changelog`, `/feedback`, `/demo`, `/outreach`.
- Backend endpoints verified with TestClient: `/ping`, `/health`, `/health/generate-test`, `/api/metrics`, `/api/evidence`.
- `git log --oneline -10` shows all Sprint 9 commits on current head.
