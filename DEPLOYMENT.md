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
- SQLite is local-only and not durable for production
- production history should use PostgreSQL through `DATABASE_URL`

## Redeploy Checklist

1. push to `main`
2. confirm Render redeploys backend
3. confirm Vercel redeploys frontend if frontend code changed
4. verify `/health`
5. verify Research, Notes, and Doubt
6. verify dashboard history

