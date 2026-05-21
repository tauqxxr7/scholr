# Scholr Deploy Checklist

This checklist now documents the live Scholr MVP deployment and the safest path for future redeploys without changing product behavior.

Deployment status:
1. backend deployed on Render
2. frontend deployed on Vercel
3. production smoke test completed for the public MVP path

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

### Option A: Manual Web Service with empty Root Directory

Use this when Render complains that `backend` does not exist or if root-directory detection feels unreliable.

Service settings:
- Root Directory: leave empty
- Environment: `Python`
- Build Command: `cd backend && pip install -r requirements.txt`
- Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
- `PYTHON_VERSION=3.12.4`

### Option B: Render Blueprint with render.yaml

This repo includes a root-level [render.yaml](/C:/Users/TAUQEER%20BHARDE/.codex/worktrees/944e/scholr/render.yaml) that defines the backend service explicitly and uses the same `cd backend && ...` commands.

Blueprint behavior:
- Runtime: `Python`
- Build Command: `cd backend && pip install -r requirements.txt`
- Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

Required environment variables:

```env
GEMINI_API_KEY=
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
2. Choose one path:
   - `New +` -> `Web Service` for Option A
   - `New +` -> `Blueprint` for Option B
3. Connect GitHub if needed.
4. Select `tauqxxr7/scholr`.
5. For Option A, leave Root Directory empty and paste the `cd backend && ...` commands.
6. For Option B, let Render detect [render.yaml](/C:/Users/TAUQEER%20BHARDE/.codex/worktrees/944e/scholr/render.yaml).
7. Set environment variables.
8. Choose the free or cheapest instance type.
9. Create the service.
10. Open `https://your-render-backend-url.onrender.com/health`.
11. Confirm `/docs` and `/api/history`.

Working deployed backend:
- [https://scholr-k9sj.onrender.com/health](https://scholr-k9sj.onrender.com/health)
- [https://scholr-k9sj.onrender.com/health/provider](https://scholr-k9sj.onrender.com/health/provider)

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
- No Clerk variables are required for the current public MVP.

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
GEMINI_API_KEY=
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
GEMINI_API_KEY=
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

Live URLs:
- Frontend: [https://scholr-coral.vercel.app](https://scholr-coral.vercel.app)
- Backend health: [https://scholr-k9sj.onrender.com/health](https://scholr-k9sj.onrender.com/health)

Current live verification:
- Frontend loads
- Backend `/health` works
- Provider health available at `/health/provider`
- Provider smoke test available at `/health/generate-test`
- Research / Notes / Doubt remain functional through fallback academic mode while provider recovery runs in the background

Recommended re-check after every redeploy:
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

### Invalid model or provider not ready

Symptom:
- `/health` or `/health/provider` shows `provider_ready: false`
- `provider_error_category` becomes `invalid_model`, `no_supported_generation_model`, `no_validated_generation_model`, `provider_timeout`, `quota_exceeded`, or `provider_5xx`

Fix:
- verify `selected_model`, `available_models_count`, `candidate_models_count`, `rejected_models_count`, and `model_selection_strategy`
- check `requests_per_minute`, `quota_cooldown_remaining_seconds`, `provider_recovery_attempts`, and `last_successful_generation_timestamp`
- confirm the Render project key has access to at least one production-safe text-generation model in the `gemini-1.5-flash` or `gemini-1.5-pro` families
- run `python backend/scripts/test_provider.py` with backend env loaded
- use `/health/generate-test` to confirm real tiny generation succeeds before declaring provider recovery complete
- force a Render redeploy after changing model or env configuration

### Restore true AI Mode

Checklist:
1. verify the Render `GEMINI_API_KEY` belongs to the intended Google AI project
2. confirm the project still has active Gemini quota
3. confirm at least one validated generation model becomes available in `/health/provider`
4. check that `/health/generate-test` returns success with a tiny generated sample
5. once provider health shows `provider_ready: true`, re-test live Research, Notes, and Doubt

Important:
- do not disable fallback mode while troubleshooting
- keep provider recovery enabled so the app remains student-safe during quota instability

### Removed auth layer

The current public MVP does not require these variables:

- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `CLERK_SECRET_KEY`
- `CLERK_JWKS_URL`
- `CLERK_JWT_ISSUER`
- `CLERK_JWT_AUDIENCE`
- `CLERK_AUTHORIZED_PARTIES`
- `AUTH_REQUIRED`

If older deployment environments still contain them, they can be removed without breaking the live public app.

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

## 7. Future Ops Roadmap

- Add centralized logging later with Sentry, Grafana, or Azure Monitor
- Keep client-side error messages user-friendly and non-sensitive
- Expand pagination only when history usage grows
- Add privacy, SEO, and analytics depth later without disturbing the MVP

## 8. Azure Future Infra Opportunity

Tauqeer has Azure for Startups access with `$1,000` in credits, but the current MVP should remain on Render + Vercel until the 10-user validation milestone shows real demand.

If that signal is strong, the next infra path to evaluate is:
- Azure App Service or Azure Container Apps for backend hosting
- Azure Database for PostgreSQL for durable production data
- Azure AI Search for semantic history and future RAG workflows
- Azure Blob Storage for exports and uploaded files
- Azure Monitor / Application Insights for observability
- Azure OpenAI / Azure AI Foundry as a future model layer
