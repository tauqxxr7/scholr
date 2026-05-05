# Scholr

AI academic workspace for BTech students that turns one prompt into research direction, revision notes, and doubt solving in under a minute.

[Live App](https://scholr-coral.vercel.app) · [Backend Health](https://scholr-k9sj.onrender.com/health)

![Next.js](https://img.shields.io/badge/Next.js-16-black?logo=next.js)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)
![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-4285F4)
![Vercel](https://img.shields.io/badge/Vercel-Live-black?logo=vercel)
![Render](https://img.shields.io/badge/Render-Live-5A67D8)

## What Scholr Is

Scholr is a focused AI academic product for engineering students, especially Indian BTech students, who need to move faster through research, revision, and concept clarification without bouncing between scattered tools.

It solves a simple but painful workflow:
- finding a useful starting point for research takes too long
- turning a topic into usable exam notes is repetitive
- doubt solving is often either too generic or too slow

Scholr packages those jobs into one clean MVP instead of trying to be a giant education platform too early.

## Demo Preview

> Demo GIF is still pending from this environment. The screenshot flow below is the current live preview.

![Scholr landing preview](screenshots/landing.png)

## Core Modules

- **Research**: generates paper direction, reading order, and realistic project gaps.
- **Notes**: turns a topic into revision-ready structured notes for exam prep.
- **Doubt**: explains concepts step by step with examples and simple language.

## Screenshots

### Landing Page
![Landing page](screenshots/landing.png)

### Research Workspace
![Research workspace](screenshots/research-workspace.png)

### Research Output
![Research output](screenshots/research-output.png)

### Notes Output
![Notes output](screenshots/notes-output.png)

### Doubt Output
![Doubt output](screenshots/doubt-output.png)

## Live MVP Status

Live MVP deployed on Vercel + Render.

Production smoke test has passed:
- landing works
- research works
- notes works
- doubt works
- backend `/health` works

Render note:
- the backend runs on Render free tier, so the first request after inactivity may cold start and take longer

## Features

- Research Assistant
- Notes Generator
- Doubt Solver
- Dashboard with recent history
- Shared SSE streaming responses
- Retry, loading, empty, and error states
- SQLite locally
- PostgreSQL-ready through `DATABASE_URL`
- Public privacy and terms pages

## Tech Stack

- Frontend: Next.js App Router, React, TypeScript, Tailwind CSS
- Backend: FastAPI, Python, SQLAlchemy
- AI: Gemini `gemini-2.5-flash`
- Local DB: SQLite
- Production DB: PostgreSQL through `DATABASE_URL`
- Hosting: Vercel + Render

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
    public/
  screenshots/
  README.md
  PROJECT_PROGRESS.md
  DEPLOY_CHECKLIST.md
  BLUEPRINT.md
  render.yaml
```

### Backend

- FastAPI app with shared Gemini generation helper
- shared SSE response helper
- `GET /health`
- `POST /api/research`
- `POST /api/notes`
- `POST /api/doubt`
- `GET /api/history`

### Frontend

- shared AI module page for Research, Notes, and Doubt
- shared API client
- responsive dashboard shell
- markdown-safe output rendering

## Run Locally

### Backend

```powershell
cd backend
venv\Scripts\activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Create `backend/.env` from `backend/.env.example`:

```env
GEMINI_API_KEY=your_real_key_here
DATABASE_URL=sqlite:///./scholr.db
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ALLOWED_ORIGIN_REGEX=https://.*\.vercel\.app
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Create `frontend/.env.local` from `frontend/.env.example`:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

## Deployment

### Frontend

- Platform: Vercel
- Root Directory: `frontend`
- Required env var:

```env
NEXT_PUBLIC_API_URL=https://scholr-k9sj.onrender.com
```

### Backend

- Platform: Render
- Root Directory: leave empty
- Build Command: `cd backend && pip install -r requirements.txt`
- Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
- `PYTHON_VERSION=3.12.4`

Required env vars:

```env
GEMINI_API_KEY=your_real_key_here
DATABASE_URL=your_postgres_connection_string
FRONTEND_URL=https://scholr-coral.vercel.app
ALLOWED_ORIGINS=https://scholr-coral.vercel.app
ALLOWED_ORIGIN_REGEX=https://.*\.vercel\.app
```

Alternative:
- a root-level `render.yaml` is also included for Blueprint-based deployment

## Roadmap

### Next

1. User validation with 10 BTech students
2. Light analytics and usage instrumentation
3. CI checks for lint, typecheck, backend validation, and build

### Later

- auth
- per-user history and saved items
- stronger production persistence with PostgreSQL
- exports
- placements and project workflows

## Suggested GitHub Topics

`ai`, `genai`, `nextjs`, `fastapi`, `gemini-api`, `typescript`, `python`, `tailwindcss`, `student-productivity`, `btech`

## Supporting Docs

- [Blueprint](BLUEPRINT.md)
- [Project Progress](PROJECT_PROGRESS.md)
- [Deployment Checklist](DEPLOY_CHECKLIST.md)
- [Screenshots Notes](screenshots/README.md)

## Security Notes

Never commit:
- `.env`
- `.env.local`
- `*.db`
- `venv`
- `.next`
- `node_modules`
- `__pycache__`
- API keys
