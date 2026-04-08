# Scholr Deploy Checklist

This checklist keeps the current MVP stable while preparing it for:
- `frontend` on Vercel
- `backend` on Railway

Do not deploy until local smoke tests are passing.

## 1. Security First

- Revoke any Gemini API key that was ever exposed.
- Create one fresh Gemini key.
- Put the new key only in `backend/.env` locally.
- Never commit:
  - `backend/.env`
  - `frontend/.env.local`
  - `backend/scholr.db`
  - `backend/venv`

## 2. Local Smoke Test

Run this before every deploy attempt:

### Backend

From `backend`:

```powershell
venv\Scripts\activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Check:

```text
http://127.0.0.1:8000/health
```

### Frontend

From `frontend`:

```powershell
npm install
npm run dev
```

Check:
- homepage
- dashboard
- research
- notes
- doubt
- history appears after generating responses
- backend unavailable state still shows a clean error

## 3. Environment Files

### Local frontend

Use `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### Local backend

Use `backend/.env`:

```env
GEMINI_API_KEY=your_real_key_here
DATABASE_URL=sqlite:///./scholr.db
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ALLOWED_ORIGIN_REGEX=https://.*\.vercel\.app
```

### Production frontend

Set this in Vercel:

```env
NEXT_PUBLIC_API_URL=https://your-railway-backend.up.railway.app
```

Important:
- `NEXT_PUBLIC_API_URL` is required in production.
- The frontend now throws a clear error if this env var is missing after deployment.

### Production backend

Set these in Railway:

```env
GEMINI_API_KEY=your_real_key_here
DATABASE_URL=your_postgres_connection_string
FRONTEND_URL=https://your-vercel-project.vercel.app
ALLOWED_ORIGINS=https://your-vercel-project.vercel.app
ALLOWED_ORIGIN_REGEX=https://.*\.vercel\.app
```

Notes:
- `FRONTEND_URL` is added automatically to backend CORS.
- `ALLOWED_ORIGINS` can be a comma-separated list if you have multiple frontend URLs.
- `ALLOWED_ORIGIN_REGEX` supports Vercel preview deployments.

## 4. Backend Deploy on Railway

Recommended target:
- one Railway service for `backend`
- one Postgres database on Railway

### Files already prepared

- `backend/Procfile`
- `backend/.env.example`

### Railway setup

1. Create a new Railway project.
2. Deploy the `backend` directory as the service root.
3. Add a Postgres database.
4. Copy the Postgres connection string into `DATABASE_URL`.
5. Add the other env vars from the production backend section.

### Start command

The included Procfile uses:

```text
python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Backend checks after deploy

Open:

```text
https://your-railway-backend.up.railway.app/health
```

Then test:
- `/api/research`
- `/api/notes`
- `/api/doubt`
- `/api/history`

## 5. Frontend Deploy on Vercel

Recommended target:
- one Vercel project rooted at `frontend`

### Files already prepared

- `frontend/.env.example`

### Vercel setup

1. Create a new Vercel project.
2. Select the repo.
3. Set the project root to `frontend`.
4. Add `NEXT_PUBLIC_API_URL` pointing to the Railway backend.
5. Deploy.

### Frontend checks after deploy

Test:
- landing page loads
- dashboard loads
- research streams
- notes streams
- doubt streams
- history loads from production backend

## 6. Database Rules

Local development:
- SQLite is fine
- the file is ignored by git

Production:
- use Postgres
- do not rely on SQLite in Railway production

Why:
- SQLite on ephemeral production filesystems is fragile
- Postgres gives persistence across deploys and restarts

## 7. Known Deployment Risks To Check

These are the main things that can break during deployment:

### Missing frontend API URL

Symptom:
- deployed frontend tries to hit nowhere or local backend

Fix:
- set `NEXT_PUBLIC_API_URL` in Vercel

### CORS errors

Symptom:
- browser blocks requests from Vercel frontend to Railway backend

Fix:
- set `FRONTEND_URL`
- set `ALLOWED_ORIGINS`
- keep `ALLOWED_ORIGIN_REGEX` for Vercel previews

### Missing Gemini key

Symptom:
- streamed readable error from backend

Fix:
- add valid `GEMINI_API_KEY` in Railway env vars

### Production database not configured

Symptom:
- history route fails or does not persist

Fix:
- connect Railway Postgres and set `DATABASE_URL`

## 8. Final Post-Deploy Smoke Test

Test exactly like a student:

1. Open landing page.
2. Open dashboard.
3. Run one Research query.
4. Run one Notes query.
5. Run one Doubt query.
6. Return to dashboard.
7. Confirm recent history appears.
8. Refresh browser.
9. Confirm history still appears.
10. Stop backend locally and verify the frontend still shows the clean unavailable state in local development.

## 9. Only After Deployment Is Stable

Then do:
- screenshots for README
- demo video
- portfolio polish
- LinkedIn launch
- auth later

Do not do these before deploy is stable:
- Clerk auth
- Placement module
- Projects module
- analytics
