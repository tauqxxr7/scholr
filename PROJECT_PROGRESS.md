# Scholr Progress Blueprint

## Vision

Scholr is an India-first academic operating system for BTech students. The product starts with one focused wedge that is easy to explain, demo, and evaluate:
- research guidance
- exam-ready notes
- doubt solving
- saved academic history

## Current Milestone

Scholr Core is now in the final shipping phase:
- Research works
- Notes works
- Doubt works
- Dashboard history works
- Shared streaming and error handling are stable
- Local and production environment behavior are separated cleanly
- Deployment setup is prepared for Vercel and Render

## What Is Finished

### Product flow

- Landing page is polished and product-positioned
- Dashboard shows recent usage and module entry points
- Research, Notes, and Doubt each stream structured output
- Copy, clear, loading, empty, and retry states are present

### Backend stability

- FastAPI startup and health route are in place
- `/docs` remains available for debugging and manual API checks
- All AI routes use one shared SSE helper
- Streaming is JSON-safe through `json.dumps`
- Every stream sends `[DONE]`
- AI/provider failures become readable streamed messages
- History save failures do not break the user response

### Data layer

- SQLite works for local development with zero setup
- Production is expected to use PostgreSQL through `DATABASE_URL`
- History is accessible through `GET /api/history`

### Deployment prep

- Backend is shaped for Render with `backend/Procfile`
- Backend falls back to SQLite only when `DATABASE_URL` is absent
- Backend CORS supports local and Vercel-hosted frontend origins
- Frontend requires `NEXT_PUBLIC_API_URL` in production
- Ignore rules cover env files, databases, caches, and build artifacts

## Shipping Checklist

1. Revoke any exposed Gemini keys.
2. Create a new production Gemini key.
3. Run the full local smoke test.
4. Deploy backend on Render first.
5. Deploy frontend on Vercel second.
6. Re-run the production smoke test.
7. Capture screenshots and the live demo URL.

## What Comes Next

After deployment is stable:
- screenshots for README
- short demo video
- recruiter-facing polish
- mentor/startup pitch walkthrough

Later, but not now:
- auth
- per-user history
- saved collections
- placements and projects

## Product Principle

The right move is still the same: make the current three-module wedge look and feel trustworthy before adding more scope.
