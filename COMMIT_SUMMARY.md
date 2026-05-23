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
