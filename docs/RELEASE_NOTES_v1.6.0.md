# Scholr v1.6.0 - Release Notes

**Released:** June 2026
**Stage:** Live MVP

## What's in this release

### Core modules
- Research: papers, reading order, research gaps with Fast and Deep modes
- Notes: structured exam-ready notes with Fast and Deep modes
- Doubt: step-by-step concept explanations with subject selector

### Production features
- Real-time SSE streaming with first-token and completion timing
- Multi-provider resilience: OpenRouter -> Gemini -> fallback academic engine
- In-memory response cache with TTL and LRU eviction
- Per-IP rate limiting (20 req/min on AI endpoints)
- PDF export of all AI responses
- Keyboard shortcuts: Ctrl+Enter, Escape, Ctrl+K
- Semantic search across history
- PostHog analytics and Sentry error monitoring
- Email waitlist capture
- /ping endpoint for UptimeRobot uptime monitoring

### Quality
- 35 backend unit tests passing
- CI green on every push (Backend CI + Frontend CI + Repo Hygiene)
- Custom 404 page, loading skeletons, backend status indicator

### Pages
- /research, /notes, /doubt, /documents
- /dashboard with history and semantic search
- /topics - BTech subject directory
- /demo - hackathon and investor demo page
- /feedback - student validation form
- /changelog, /status, /outreach

## Known limitations
- Auth not yet enabled (planned for v1.7.0)
- PostgreSQL migration ready but SQLite in use on free tier
- Document intelligence backend-only (frontend upload planned for v1.7.0)

## Built by
Tauqeer Bharde - BTech AI & Data Science student
