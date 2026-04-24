# Scholr

> AI-powered academic productivity platform for research guidance, smart notes, and doubt solving.

[![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Gemini](https://img.shields.io/badge/Gemini_API-1A73E8?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)

[![Source Code](https://img.shields.io/badge/Source_Code-111827?style=for-the-badge&logo=github&logoColor=white)](https://github.com/tauqxxr7/scholr)

## Overview

Scholr is an AI-powered academic productivity platform built around a focused student workflow: research support, notes generation, and doubt solving. The goal is simple: help a learner turn a topic into useful academic output in under a minute.

Rather than shipping as a generic student chatbot, Scholr is positioned as a product-led AI application with a real frontend, a structured backend, streaming model responses, and saved activity history.

## Product Positioning

**Scholr is an India-first academic operating system for BTech students.**

It is designed to show how AI can be applied to practical educational workflows with better UX, faster output, and a more intentional product surface than a basic prompt box.

## Current Capabilities

- Research guidance
- Exam-ready notes generation
- Step-by-step doubt solving
- Streaming AI responses
- Activity history and dashboard view

### Working Routes

- `/research`
- `/notes`
- `/doubt`
- `/dashboard`

## Tech Stack

### Frontend

- Next.js App Router
- TypeScript
- Tailwind CSS
- shadcn/ui
- React Markdown

### Backend

- FastAPI
- Python
- Google Generative AI SDK
- SQLAlchemy
- SQLite for local development
- SSE streaming responses

### Deployment Direction

- Vercel for frontend
- Render or Railway for backend
- PostgreSQL planned for production

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
  DEPLOY_CHECKLIST.md
  README.md
```

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/tauqxxr7/scholr.git
cd scholr
```

### 2. Start the backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
python -m uvicorn main:app --reload --port 8000
```

Health check: `http://127.0.0.1:8000/health`

### 3. Start the frontend

Open a new terminal:

```bash
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

Frontend: `http://localhost:3000`

## Environment Variables

### `backend/.env`

```env
GEMINI_API_KEY=replace_with_real_gemini_key
DATABASE_URL=sqlite:///./scholr.db
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ALLOWED_ORIGIN_REGEX=https://.*\.vercel\.app
```

### `frontend/.env.local`

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

## Demo Flow

1. Open the landing page.
2. Visit the dashboard.
3. Run a research prompt.
4. Generate notes for a technical concept.
5. Use the doubt solver.
6. Return to the dashboard and show saved history.

### Suggested Prompts

- Research: `Machine Learning for traffic prediction`
- Notes: `Operating System deadlock`
- Doubt subject: `DBMS`
- Doubt question: `What is normalization and why do we use it?`

## Screenshots

### Landing Page

`Add screenshot: docs/screenshots/landing.png`

### Dashboard

`Add screenshot: docs/screenshots/dashboard.png`

### Research / Notes / Doubt Workflow

`Add screenshot: docs/screenshots/modules.png`

## Current Status

### Finished

- Shared streaming pattern across all AI modules
- Cleaner dashboard and module pages
- SQLite-based local history
- Product-ready MVP shell

### Next

- Mobile polish and output readability improvements
- Better backend error handling
- Authentication and user accounts
- Production deployment
- PostgreSQL migration

## Project Docs

- Progress summary: `PROJECT_PROGRESS.md`
- Deploy prep: `DEPLOY_CHECKLIST.md`

## Security Notes

Never commit:

- `backend/.env`
- `frontend/.env.local`
- `backend/scholr.db`
- `backend/venv`
- API keys

If a Gemini key is exposed, revoke and rotate it immediately.
