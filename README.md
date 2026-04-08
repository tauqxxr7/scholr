# Scholr

Scholr is an AI-powered academic operating system for BTech students.

The current MVP focuses on one polished wedge:
- Research guidance
- Exam-ready notes
- Step-by-step doubt solving

It is built to help a student turn a topic into useful academic output in under a minute.

## Current Status

Scholr Core is working locally with:
- Next.js frontend
- FastAPI backend
- Gemini streaming responses
- SQLite history storage
- Dashboard showing recent activity

Working routes:
- `/research`
- `/notes`
- `/doubt`
- `/dashboard`

## Product Positioning

This is not being built as "just another AI app for students."

The sharper pitch is:

`Scholr is an India-first academic operating system for BTech students.`

## Tech Stack

Frontend:
- Next.js App Router
- TypeScript
- Tailwind CSS
- shadcn/ui
- React Markdown

Backend:
- FastAPI
- Python
- Google Generative AI SDK
- SQLAlchemy
- SQLite for local development

Deployment target:
- Vercel for frontend
- Railway or Render for backend
- Postgres later for production

## Repository Structure

```text
scholr/
  backend/
    agents/
    db/
    models/
    routers/
    main.py
  frontend/
    app/
    components/
    lib/
  PROJECT_PROGRESS.md
  README.md
```

## Local Setup

### 1. Backend

From `backend`:

```powershell
venv\Scripts\activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Create `backend/.env` with:

```env
GEMINI_API_KEY=your_real_key_here
DATABASE_URL=sqlite:///./scholr.db
```

Health check:

```text
http://127.0.0.1:8000/health
```

### 2. Frontend

From `frontend`:

```powershell
npm install
npm run dev
```

Create `frontend/.env.local` with:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Frontend URL:

```text
http://localhost:3000
```

## Demo Flow

Use this exact flow when showing the MVP:

1. Open the landing page.
2. Go to the dashboard.
3. Run one Research query.
4. Run one Notes query.
5. Run one Doubt query.
6. Return to dashboard and show saved history.

Suggested sample prompts:
- Research: `Machine Learning for traffic prediction`
- Notes: `Operating System deadlock`
- Doubt:
  - Subject: `DBMS`
  - Question: `What is normalization and why do we use it?`

## What Is Finished

- Shared SSE streaming pattern across all 3 AI modules
- Cleaner module pages with loading, clear, and copy actions
- SQLite-based local search history
- Dashboard activity feed
- Product-ready landing page and shell

## What Comes Next

- UI polish pass for mobile and output readability
- Better backend error messaging
- Clerk auth reintroduced carefully
- Deployment to Vercel and Railway
- Postgres migration for production

## Security Notes

Never commit or paste:
- `backend/.env`
- `frontend/.env.local`
- `backend/scholr.db`
- `backend/venv`
- API keys

If any Gemini key is exposed, revoke it immediately and create a new one.

## Recommended Git Milestone

This is the right milestone to commit with:

```text
Stabilize Scholr MVP with streaming AI modules and local history
```

## Project Docs

- Progress summary: `PROJECT_PROGRESS.md`
- Deploy prep: `DEPLOY_CHECKLIST.md`
