# Scholr Deploy Checklist

## Before You Deploy

- Revoke any Gemini key that was ever exposed.
- Put the fresh key only in `backend/.env`.
- Confirm these local routes work:
  - `/research`
  - `/notes`
  - `/doubt`
  - `/dashboard`
- Confirm history saves and persists after browser refresh.

## Repo Hygiene

Make sure these are not tracked:
- `backend/.env`
- `frontend/.env.local`
- `backend/venv/`
- `backend/__pycache__/`
- `frontend/.next/`
- `backend/scholr.db`

Run:

```powershell
git status
```

If junk files are tracked, untrack them before deployment.

## Frontend Deploy

Target:
- Vercel

Required env:

```env
NEXT_PUBLIC_API_URL=https://your-backend-url
```

Checks:
- landing page loads
- dashboard loads
- module pages render without console errors
- production frontend points to production backend

## Backend Deploy

Target:
- Railway or Render

Required env:

```env
GEMINI_API_KEY=your_real_key
DATABASE_URL=your_database_url
```

For first deploy, SQLite is okay locally only.
For production, use Postgres.

Checks:
- `/health` returns success
- `/api/research` streams
- `/api/notes` streams
- `/api/doubt` streams
- `/api/history` returns stored items

## Production Database

Local:
- SQLite

Production:
- Postgres

Why:
- safer for multi-user usage
- persistent managed storage
- easier scaling later

## Final Smoke Test

After deploy, test like a real user:

1. Open landing page.
2. Go to dashboard.
3. Run a Research query.
4. Run a Notes query.
5. Run a Doubt query.
6. Return to dashboard.
7. Confirm recent history appears.
8. Refresh the page.
9. Confirm the app still behaves cleanly.

## Only After Deploy Is Stable

Then do:
- auth with Clerk
- per-user history
- save/export actions
- placement and project modules
