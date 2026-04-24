# Scholr

Scholr is an AI-powered academic operating system for BTech students. The current MVP focuses on one sharp wedge: turn any engineering topic into research direction, exam-ready notes, and clear doubt solving in under a minute.

## Product Overview

Scholr is built around the real workflow of Indian engineering students:
- discover what to read
- understand what matters for exams
- unblock doubts quickly
- keep a usable history of what was generated

Instead of trying to ship every student feature at once, the product starts with one polished core experience:
- Research
- Notes
- Doubt
- Dashboard history

## Live Demo

- Frontend: `Add your Vercel URL here`
- Backend health: `Add your Render backend /health URL here`

## Screenshots

Add these after deployment:
- `Landing page`
- `Dashboard`
- `Research module`
- `Notes module`
- `Doubt module`

## Features

- Streaming AI responses across Research, Notes, and Doubt
- Shared SSE handling with JSON-safe chunking and `[DONE]` completion
- Local history storage for completed generations
- Product-style dashboard with recent activity
- Helpful empty, loading, success, and retry states
- Production-aware frontend API handling
- Deployment-ready backend CORS and environment handling

## Architecture

```text
scholr/
  backend/
    agents/
    db/
    models/
    routers/
    main.py
    Procfile
    runtime.txt
  frontend/
    app/
    components/
    lib/
  README.md
  PROJECT_PROGRESS.md
  DEPLOY_CHECKLIST.md
```

### Frontend

- Next.js App Router
- TypeScript
- Tailwind CSS v4
- shadcn/ui
- React Markdown

### Backend

- FastAPI
- Google Generative AI SDK
- SQLAlchemy
- SQLite for local development
- PostgreSQL through `DATABASE_URL` in production

## Tech Stack

- Frontend: Next.js, React, TypeScript, Tailwind CSS, shadcn/ui
- Backend: FastAPI, Python, SQLAlchemy
- AI: Gemini 2.5 Flash
- Local storage: SQLite
- Production storage: PostgreSQL when available
- Deployment: Vercel + Render

## Current Status

Scholr Core is stable locally and prepared for deployment.

Working routes:
- `/`
- `/dashboard`
- `/research`
- `/notes`
- `/doubt`
- `/api/history`
- `/health`
- `/docs`

## Local Setup

### Backend

From `backend`:

```powershell
venv\Scripts\activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Create `backend/.env`:

```env
GEMINI_API_KEY=your_real_key_here
DATABASE_URL=sqlite:///./scholr.db
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ALLOWED_ORIGIN_REGEX=https://.*\.vercel\.app
```

Backend checks:
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

### Frontend

From `frontend`:

```powershell
npm install
npm run dev
```

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

Frontend URL:
- `http://localhost:3000`

## Deployment Setup Summary

### Render backend

- Root Directory: `backend`
- Build Command:

```text
pip install -r requirements.txt
```

- Start Command:

```text
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Required env vars:

```env
GEMINI_API_KEY=your_real_key_here
DATABASE_URL=your_render_postgres_connection_string
FRONTEND_URL=https://your-vercel-project.vercel.app
ALLOWED_ORIGINS=https://your-vercel-project.vercel.app
ALLOWED_ORIGIN_REGEX=https://.*\.vercel\.app
```

### Vercel frontend

- Root Directory: `frontend`

Required env var:

```env
NEXT_PUBLIC_API_URL=https://your-render-backend-url.onrender.com
```

If `NEXT_PUBLIC_API_URL` changes in Vercel, redeploy so the new value takes effect.

## Demo Flow

Use this sequence when showing the product:

1. Open the landing page.
2. Open the dashboard.
3. Run one Research query.
4. Run one Notes query.
5. Run one Doubt query.
6. Return to dashboard and show recent history.

Suggested prompts:
- Research: `Machine Learning for traffic prediction`
- Notes: `Operating System deadlock`
- Doubt:
  - Subject: `DBMS`
  - Question: `What is normalization and why do we use it?`

## Deployment Notes

- Render free web services can sleep after inactivity and may take around a minute to spin back up.
- Render free web services use an ephemeral filesystem, so SQLite should be treated as local-only and not relied on for production persistence.
- If Render PostgreSQL free is available, use it through `DATABASE_URL`.
- If free Postgres is not available, you can still deploy the app, but document clearly that production history persistence is optional or temporary.

## Roadmap

Near-term:
- Deploy backend on Render
- Deploy frontend on Vercel
- Capture screenshots and a short demo video

Later:
- Reintroduce auth carefully
- Add per-user history
- Add saved items and exports
- Add placement and project flows only after the current wedge is clearly sticky

## Security Notes

Never commit:
- `backend/.env`
- `frontend/.env.local`
- `*.db`
- `venv`
- `.next`
- `__pycache__`
- API keys

If a Gemini key is ever exposed, revoke it immediately and create a new one.

## Project Docs

- `PROJECT_PROGRESS.md`
- `DEPLOY_CHECKLIST.md`
