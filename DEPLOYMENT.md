# Scholr Deployment

## Live Deployment

- Frontend: [https://scholr-coral.vercel.app](https://scholr-coral.vercel.app)
- Backend health: [https://scholr-k9sj.onrender.com/health](https://scholr-k9sj.onrender.com/health)

## Frontend Deployment

- Platform: Vercel
- Root Directory: `frontend`

Required environment variable:

```env
NEXT_PUBLIC_API_URL=https://scholr-k9sj.onrender.com
```

No Clerk or auth-specific frontend variables are required for the current public MVP.

## Backend Deployment

- Platform: Render
- Root Directory: leave empty
- Build Command: `cd backend && pip install -r requirements.txt`
- Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
- `PYTHON_VERSION=3.12.4`

Required environment variables:

```env
GEMINI_API_KEY=
DATABASE_URL=your_postgres_connection_string
FRONTEND_URL=https://scholr-coral.vercel.app
ALLOWED_ORIGINS=https://scholr-coral.vercel.app
ALLOWED_ORIGIN_REGEX=https://.*\.vercel\.app
```

Set `GEMINI_API_KEY` in Render with a real Gemini API key. Keep it blank in docs and tracked files.

## Public Access

Scholr currently ships as a public-access academic workspace. These routes should open directly without sign-in:

- `/`
- `/dashboard`
- `/research`
- `/notes`
- `/doubt`
- `/documents`

## Provider Health Diagnostics

`/health` returns safe provider metadata:

- `provider_configured`
- `provider_ready`
- `model_name`
- `provider_error_category`
- `provider_sdk_version`

This does not expose secrets, but it makes production incidents easier to triage.

## Provider Troubleshooting

If the live app shows `AI provider error. Please retry.`:

1. confirm `GEMINI_API_KEY` is present in Render
2. confirm the Google AI project still has Gemini API quota and access
3. check `/health` for the startup-selected `model_name`
4. verify the backend has fully redeployed after code or env changes
5. confirm the fallback model chain is still available to the project

## Known Production Realities

- Render free tier can cold start after inactivity
- Render's normal filesystem is ephemeral, so a relative SQLite file such as `./scholr.db` will be wiped on deploy
- if SQLite is used in production, mount a Render Persistent Disk at `/data` and set `SQLITE_PATH=/data/scholr.db`
- for durable production history without disk management, set `DATABASE_URL` to a PostgreSQL connection string

## Persistence On Render

Scholr supports two production-safe persistence paths:

1. Render Persistent Disk with SQLite:
   - mount the disk at `/data`
   - set `SQLITE_PATH=/data/scholr.db`
   - leave `DATABASE_URL` blank unless using PostgreSQL

2. PostgreSQL:
   - set `DATABASE_URL` to a `postgresql://...` connection string
   - Scholr will use PostgreSQL instead of SQLite when this environment variable starts with `postgresql`

Do not rely on `./scholr.db` for production history on Render.

## Database

Set `DATABASE_URL` to a PostgreSQL connection string on Render to use PostgreSQL. If not set, Scholr defaults to SQLite at `SQLITE_PATH` (`/data/scholr.db`). Render provides `postgres://` URLs; the engine automatically rewrites these to `postgresql://` for SQLAlchemy compatibility.

## Semantic History Search

`/api/search` uses lightweight deterministic embeddings by default so Render health checks stay fast. Set `ENABLE_SENTENCE_TRANSFORMERS=true` only on a larger instance where model downloads and memory are acceptable.

## Redeploy Checklist

1. push to `main`
2. confirm Render redeploys backend
3. confirm Vercel redeploys frontend if frontend code changed
4. verify `/health`
5. verify Research, Notes, and Doubt
6. verify dashboard history

