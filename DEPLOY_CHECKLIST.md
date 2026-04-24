# Scholr Deploy Checklist

This runbook is for shipping the current MVP on the cheapest practical path without changing product behavior.

Deploy order:
1. backend on Render
2. frontend on Vercel
3. production smoke test

Do not deploy until the full local smoke test passes.

## 1. Security First

- Revoke any Gemini API key that was ever exposed.
- Create one fresh Gemini key.
- Put the new key only in `backend/.env` locally and in Render environment variables for production.
- Never commit:
  - `backend/.env`
  - `frontend/.env.local`
  - `*.db`
  - `venv`
  - `.next`
  - `__pycache__`

## 2. Local Smoke Test Before Deployment

### Start backend

From `backend`:

```powershell
venv\Scripts\activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Verify:
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

### Start frontend

From `frontend`:

```powershell
npm install
npm run dev
```

Verify:
- homepage loads
- dashboard loads
- Research works
- Notes works
- Doubt works
- dashboard history appears after generation
- backend unavailable state still shows a clean message

## 3. Local Environment Files

### backend/.env

```env
GEMINI_API_KEY=your_real_key_here
DATABASE_URL=sqlite:///./scholr.db
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ALLOWED_ORIGIN_REGEX=https://.*\.vercel\.app
```

### frontend/.env.local

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

## 4. Render Backend Deployment

### Required service shape

- GitHub repo: `tauqxxr7/scholr`
- Root Directory: `backend`
- Build Command:

```text
pip install -r requirements.txt
```

- Start Command:

```text
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Required backend environment variables

```env
GEMINI_API_KEY=your_real_key_here
DATABASE_URL=your_render_postgres_connection_string
FRONTEND_URL=https://your-vercel-project.vercel.app
ALLOWED_ORIGINS=https://your-vercel-project.vercel.app
ALLOWED_ORIGIN_REGEX=https://.*\.vercel\.app
```

Notes:
- If you do not provision Render Postgres, the backend will fall back to SQLite.
- That fallback is acceptable for local development only.
- Render web services use an ephemeral filesystem, so SQLite data can be lost on redeploy, restart, or free-tier spin-down.

### Optional database path

Preferred:
- use Render PostgreSQL through `DATABASE_URL`

Fallback:
- deploy without `DATABASE_URL` only if you are okay with non-persistent or temporary production history

### Exact Render click order

1. Open Render.
2. Click `New +`.
3. Choose `Web Service`.
4. Connect GitHub if needed.
5. Select `tauqxxr7/scholr`.
6. Set the service name you want.
7. Set `Root Directory` to `backend`.
8. Set `Environment` to `Python`.
9. Set `Build Command` to `pip install -r requirements.txt`.
10. Set `Start Command` to `uvicorn main:app --host 0.0.0.0 --port $PORT`.
11. Set the required backend env vars.
12. Choose the cheapest/free instance type available.
13. Create the service.
14. Open the public backend URL and verify `/health`.

### Render free-tier notes

- Free web services can sleep after inactivity.
- The next request can take roughly a minute to spin the service back up.
- Free web services use an ephemeral filesystem.
- If Render free Postgres is available, use it.
- If free Postgres is not available, document clearly that production history persistence is optional or temporary.
- Render’s free Postgres offering can have storage or lifetime limitations; check the current Render dashboard plan details before depending on it.

### Backend verification

Check:
- `https://your-render-backend-url.onrender.com/health`

Then manually confirm:
- `/api/history`
- `/docs`

## 5. Vercel Frontend Deployment

### Required service shape

- GitHub repo: `tauqxxr7/scholr`
- Root Directory: `frontend`

### Required frontend environment variables

```env
NEXT_PUBLIC_API_URL=https://your-render-backend-url.onrender.com
```

Important:
- `NEXT_PUBLIC_API_URL` is required in production.
- If you change it in Vercel later, create a new deployment so the new value is used.

### Exact Vercel click order

1. Open Vercel.
2. Click `Add New...` then `Project`.
3. Import `tauqxxr7/scholr`.
4. Set `Root Directory` to `frontend`.
5. Open `Environment Variables`.
6. Add `NEXT_PUBLIC_API_URL` and set it to the Render backend URL.
7. Deploy.
8. If you update env vars later, redeploy.

## 6. Production Rules

### Database

Local:
- SQLite is allowed

Production:
- Prefer PostgreSQL through `DATABASE_URL`
- Do not rely on SQLite for persistent production history on Render

### CORS

Backend CORS must include:
- the deployed Vercel frontend URL through `FRONTEND_URL`
- any explicit frontend origins through `ALLOWED_ORIGINS`
- preview support through `ALLOWED_ORIGIN_REGEX`

### Frontend API base URL

Local:
- frontend can use `http://127.0.0.1:8000`

Production:
- frontend must use the deployed Render backend URL

## 7. Common Errors And Fixes

### Missing NEXT_PUBLIC_API_URL

Symptom:
- deployed frontend cannot reach the backend

Fix:
- add `NEXT_PUBLIC_API_URL` in Vercel
- redeploy

### Incorrect CORS

Symptom:
- browser blocks requests from frontend to backend

Fix:
- set `FRONTEND_URL`
- set `ALLOWED_ORIGINS`
- keep `ALLOWED_ORIGIN_REGEX`

### Missing Gemini key

Symptom:
- readable streamed provider or config errors from backend

Fix:
- set `GEMINI_API_KEY` in Render

### Missing production database

Symptom:
- history does not persist or history route fails after restarts or redeploys

Fix:
- provision Render Postgres and set `DATABASE_URL`

### Cold start on free tier

Symptom:
- first request after idle is slow

Fix:
- wait for Render to spin the service back up
- document this in the demo walkthrough

## 8. Production Smoke Test

Run this in the live app after both deploys:

1. Open landing page.
2. Open dashboard.
3. Run Research with `Machine Learning for traffic prediction`.
4. Run Notes with `Operating System deadlock`.
5. Run Doubt with:
   - Subject: `DBMS`
   - Question: `What is normalization and why do we use it?`
6. Return to dashboard.
7. Confirm recent history appears.
8. Refresh the page.
9. Confirm history still appears.
10. Re-open the backend `/health` URL and confirm it still responds.

## 9. After Deployment Stabilizes

Then do:
- add screenshots to README
- record a short demo video
- polish the GitHub repo description
- share the live demo

Still do not do yet:
- auth
- placements
- projects
- analytics
