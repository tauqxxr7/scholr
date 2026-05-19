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

## Backend Deployment

- Platform: Render
- Root Directory: leave empty
- Build Command: `cd backend && pip install -r requirements.txt`
- Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
- `PYTHON_VERSION=3.12.4`

Required environment variables:

```env
GEMINI_API_KEY=your_real_key_here
DATABASE_URL=your_postgres_connection_string
FRONTEND_URL=https://scholr-coral.vercel.app
ALLOWED_ORIGINS=https://scholr-coral.vercel.app
ALLOWED_ORIGIN_REGEX=https://.*\.vercel\.app
```

## Provider Health Diagnostics

`/health` returns safe provider metadata:

- `provider_configured`
- `provider_ready`
- `model_name`
- `provider_error_category`
- `provider_sdk_version`

This does not expose secrets, but it makes production incidents easier to triage.

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

