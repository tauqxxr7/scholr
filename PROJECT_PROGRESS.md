# Scholr Progress Blueprint

## Vision
Scholr is an India-first academic operating system for BTech students. The immediate wedge is simple and strong: research guidance, notes generation, and doubt solving with streaming AI responses.

## What Is Finished
- Frontend MVP is running on Next.js with a landing page, dashboard shell, and three working product routes:
  - `/research`
  - `/notes`
  - `/doubt`
- Backend MVP is running on FastAPI with Gemini-powered streaming responses.
- All three modules now use one consistent SSE response pattern:
  - JSON-safe chunk streaming
  - graceful fallback errors
  - `[DONE]` completion signal
- Local SQLite history is now part of the architecture:
  - every successful research, notes, and doubt response is stored
  - `GET /api/history` returns recent activity
- Dashboard now reflects the real product state by showing recent saved responses.
- Clerk has been intentionally removed for the current milestone so the core experience stays stable.

## What Needs Work Next
- Product quality
  - stronger prompt tuning for each module
  - better markdown rendering for tables, code, and dense academic output
  - polish loading states and empty states further
- Platform features
  - bring back auth the right way
  - add per-user history once auth exists
  - add saved items and export flows
- Deployment
  - frontend to Vercel
  - backend to Railway or Render
  - move from SQLite to Postgres in production
- Growth wedge
  - landing page copy for pitches
  - demo data
  - analytics and feedback capture

## Recommended Build Order
1. Keep Research, Notes, and Doubt stable locally.
2. Verify history flow and dashboard reliability.
3. Push this working milestone to Git.
4. Add auth only after the core loop is solid.
5. Deploy after local verification passes.

## Git Recommendation
Push now, not only at the end.

Reason:
- this is already a meaningful milestone
- you now have a real working core product, not just scaffold code
- pushing after each stable milestone is safer and looks better in project history

Recommended commit message:

`Stabilize Scholr MVP with streaming AI modules and local history`

## Current Milestone
Scholr Core is locally functional:
- Research works
- Notes works
- Doubt works
- History works
- Dashboard reflects real usage

That is the right point to commit and push before adding auth, deployment, or new modules.
