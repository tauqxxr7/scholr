# Scholr

> AI-powered academic productivity platform for research guidance, smart notes, and doubt solving.

[![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Gemini](https://img.shields.io/badge/Gemini_API-1A73E8?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)

[![Source Code](https://img.shields.io/badge/Source_Code-111827?style=for-the-badge&logo=github&logoColor=white)](https://github.com/tauqxxr7/scholr)

## Problem

Students often switch between disconnected tools for researching a topic, generating notes, and resolving doubts. That breaks focus and makes academic workflows slower than they should be.

## Solution

Scholr is an AI-powered academic productivity platform designed to help students generate notes, solve doubts, research faster, and track learning history. It brings multiple learning workflows into one product-style interface with persistent activity tracking and a scalable product direction.

## Features

- Notes generation
- Doubt solving
- Research assistant workflow
- Persistent history
- Streaming AI responses
- Dashboard-based activity view

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

## Architecture

```text
User -> Next.js frontend -> FastAPI backend -> Gemini-powered agents -> response streaming -> persistent history -> dashboard UI
```

Scholr is built with production-style project structure, separate frontend/backend architecture, and a direction that can scale beyond a single MVP feature.

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

## Setup

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
GEMINI_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///./scholr.db
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ALLOWED_ORIGIN_REGEX=https://.*\.vercel\.app
```

### `frontend/.env.local`

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

## Screenshots / Demo

- Landing page: `Add screenshot or demo GIF here`
- Dashboard: `Add screenshot or demo GIF here`
- Research / notes / doubt workflow: `Add screenshot or demo GIF here`

## Live Demo

- Frontend: `Deployment in progress`
- Backend: `Deployment in progress`
- Source code: `https://github.com/tauqxxr7/scholr`

## Future Improvements

- Authentication and user accounts
- PostgreSQL migration
- Better mobile polish
- Output readability improvements
- More academic workflows around revision and planning

## Author

Built by **Tauqeer Bharde** as a flagship AI/full-stack project focused on usability, maintainability, and a strong product direction.

## Suggested GitHub Topics

`ai, genai, llm, gemini-api, full-stack, nextjs, fastapi, python, react, tailwindcss`
