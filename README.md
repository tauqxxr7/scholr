# Scholr

> AI-powered academic productivity platform for notes generation, doubt solving, research assistance, and learning history tracking.

[![Next.js](https://img.shields.io/badge/Next.js-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-0F172A?style=for-the-badge&logo=tailwindcss&logoColor=38BDF8)](https://tailwindcss.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Gemini](https://img.shields.io/badge/Gemini_API-1A73E8?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)

[![Source Code](https://img.shields.io/badge/Source_Code-111827?style=for-the-badge&logo=github&logoColor=white)](https://github.com/tauqxxr7/scholr)

## Problem

Students often jump between separate tools for research, notes, clarification, and revision history. That fragmentation makes learning slower and creates friction when turning a topic into usable academic output.

## Solution

Scholr is an AI-powered academic productivity platform designed to help students generate notes, solve doubts, research faster, and track learning history.

Built as a scalable product with separation between frontend, backend, and AI layers.

## Features

- Research assistant flow for fast topic exploration
- Notes generation for study-ready summaries
- Doubt solving with step-by-step explanations
- Persistent learning history for recent activity and retrieval
- Product-ready dashboard structure for future student workflows

## Architecture

```text
Student → Next.js Frontend → FastAPI Backend → Gemini AI Layer → Learning History
```

This repository is structured like a production-style product instead of a single prompt demo, with clear service boundaries and room for future scale.

## Tech Stack

- Frontend: Next.js, TypeScript, Tailwind CSS, shadcn/ui
- Backend: FastAPI, Python
- AI Layer: Gemini API
- Data Layer: SQLite for local development
- Deployment target: Vercel frontend + Render/Railway backend

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/tauqxxr7/scholr.git
cd scholr
```

### 2. Start the backend

```powershell
cd backend
venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env
python -m uvicorn main:app --reload --port 8000
```

### 3. Start the frontend

Open a new terminal:

```powershell
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

### 4. Open the app

- Frontend: `http://localhost:3000`
- Backend: `http://127.0.0.1:8000`
- Health check: `http://127.0.0.1:8000/health`

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

## Screenshots

Screenshots coming soon.

## Deployment Status

- Frontend: `Deployment in progress`
- Backend: `Deployment in progress`

## Roadmap

- Authentication
- Persistent chat/history
- Notes export
- Dashboard analytics
- Better prompt orchestration
- Deployment

## Author / Contact

Built by **Tauqeer Bharde** as a flagship AI product focused on education, product usability, and deployable architecture.

- GitHub: `https://github.com/tauqxxr7`
- LinkedIn: `https://www.linkedin.com/in/tauqeer-sameer-85b868235`

## Suggested GitHub Topics

`ai, genai, llm, gemini-api, nextjs, fastapi, python, typescript, tailwindcss, student-productivity, full-stack`
