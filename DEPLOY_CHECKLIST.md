# Scholr Deploy Checklist

This checklist ships the clean Scholr MVP without changing product behavior.

Deploy order:
1. backend on Render
2. frontend on Vercel
3. production smoke test

## 1. Local Smoke Test

### Backend

From `backend`:

```powershell
venv\Scripts\activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Verify:
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

### Frontend

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

## 2. Render Backend Deployment

Service settings:
- Root Directory: `backend`
- Environment: `Python`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

Required environment variables:

```env
GEMINI_API_KEY=your_real_key_here
DATABASE_URL=your_postgres_connection_string
FRONTEND_URL=https://your-vercel-project.vercel.app
ALLOWED_ORIGINS=https://your-vercel-project.vercel.app
ALLOWED_ORIGIN_REGEX=https://.*\.vercel\.app
```

Notes:
- If `DATABASE_URL` is missing, the backend falls back to SQLite.
- That fallback is acceptable locally, not for durable production history.
- Render free web services may sleep after inactivity.
- Render free web services use an ephemeral filesystem, so SQLite data can disappear on restart or redeploy.
- If Render PostgreSQL free is available, use it.
- If free Postgres is unavailable, production history should be treated as optional or temporary.

Exact steps:
1. Open Render.
2. Click `New +`.
3. Choose `Web Service`.
4. Connect GitHub if needed.
5. Select `tauqxxr7/scholr`.
6. Set `Root Directory` to `backend`.
7. Set `Environment` to `Python`.
8. Set `Build Command` to `pip install -r requirements.txt`.
9. Set `Start Command` to `uvicorn main:app --host 0.0.0.0 --port $PORT`.
10. Add the required environment variables.
11. Choose the free or cheapest instance type.
12. Create the service.
13. Open `https://your-render-backend-url.onrender.com/health`.
14. Confirm `/docs` and `/api/history`.

## 3. Vercel Frontend Deployment

Project settings:
- Root Directory: `frontend`

Required environment variable:

```env
NEXT_PUBLIC_API_URL=https://your-render-backend-url.onrender.com
```

Important:
- `NEXT_PUBLIC_API_URL` is required in production.
- Vercel env var changes require a redeploy.

Exact steps:
1. Open Vercel.
2. Click `Add New...` then `Project`.
3. Import `tauqxxr7/scholr`.
4. Set `Root Directory` to `frontend`.
5. Add `NEXT_PUBLIC_API_URL`.
6. Deploy.
7. If you change env vars later, redeploy.

## 4. Environment Variables

### Local backend

```env
GEMINI_API_KEY=your_real_key_here
DATABASE_URL=sqlite:///./scholr.db
FRONTEND_URL=http://localhost:3000
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ALLOWED_ORIGIN_REGEX=https://.*\.vercel\.app
```

### Local frontend

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

### Production backend

```env
GEMINI_API_KEY=your_real_key_here
DATABASE_URL=your_postgres_connection_string
FRONTEND_URL=https://your-vercel-project.vercel.app
ALLOWED_ORIGINS=https://your-vercel-project.vercel.app
ALLOWED_ORIGIN_REGEX=https://.*\.vercel\.app
```

### Production frontend

```env
NEXT_PUBLIC_API_URL=https://your-render-backend-url.onrender.com
```

## 5. Production Smoke Test

1. Open the live landing page.
2. Open the live dashboard.
3. Run Research with `Machine Learning for traffic prediction`.
4. Run Notes with `Operating System deadlock`.
5. Run Doubt with:
   - Subject: `DBMS`
   - Question: `What is normalization and why do we use it?`
6. Return to dashboard.
7. Confirm history appears.
8. Refresh the page.
9. Confirm history still appears.
10. Re-open backend `/health`.

## 6. Common Errors And Fixes

### Missing NEXT_PUBLIC_API_URL

Symptom:
- frontend cannot reach backend in production

Fix:
- set `NEXT_PUBLIC_API_URL` in Vercel
- redeploy

### CORS failure

Symptom:
- browser blocks frontend requests to backend

Fix:
- set `FRONTEND_URL`
- set `ALLOWED_ORIGINS`
- keep `ALLOWED_ORIGIN_REGEX`

### Missing Gemini key

Symptom:
- readable streamed provider/config error from backend

Fix:
- set `GEMINI_API_KEY` in Render

### Missing PostgreSQL

Symptom:
- history disappears after restart or redeploy

Fix:
- provision Render PostgreSQL
- set `DATABASE_URL`

### Render cold start

Symptom:
- first request after idle is slow

Fix:
- wait for Render to wake the service
- mention this during demos
