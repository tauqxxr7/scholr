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
- Message: `chore: sprint 2 retry — final verification and commit summary`
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
