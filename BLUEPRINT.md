# Scholr Blueprint

## Vision
Build Scholr into the academic operating system BTech students open when they need fast research direction, usable notes, and clear doubt solving without wasting hours across random tabs, PDFs, and videos.

## Core Assumption
Students will return if Scholr consistently saves time on high-friction academic work and feels more reliable than generic AI chat for engineering study flows.

## The Real Problem
- BTech students lose time switching between search, YouTube, notes apps, and scattered AI tools.
- Generic AI tools do not package answers in exam-ready, research-aware formats.
- Students need speed, structure, and confidence more than raw model capability.

## Early Adopter Profile
- Indian BTech students in years 2 through 4
- Students preparing for internals, end-sem exams, viva, mini-projects, and final-year idea exploration
- Users who already combine ChatGPT, Gemini, YouTube, and Google Scholar but want one sharper workflow

## Competitor Map

### Direct
- ChatGPT
- Gemini
- Perplexity
- Study-oriented AI note generators

### Indirect
- Google Scholar
- Notion templates
- YouTube educators
- Telegram and WhatsApp peer groups
- University notes websites

## MVP Scope
- Research Assistant
- Notes Generator
- Doubt Solver
- Dashboard with saved history
- Clean deployment flow on Render + Vercel

## Cut For Now
- Authentication
- Placements module
- Projects module
- Paid plans
- Heavy analytics
- Collaboration features
- File upload pipelines

## Validation Criteria
- A student can complete one useful research, notes, or doubt workflow in under 60 seconds
- History persists when a real database is configured
- The app works on mobile and desktop
- The product can be demoed live without confusing states or broken flows
- Recruiters and mentors can understand the product and architecture from the repo alone

## Two-Week Launch Plan

### Week 1
- Freeze MVP scope
- Validate local flow and production deployment
- Capture screenshots and demo video
- Share with 10 target students for structured feedback

### Week 2
- Track repeated prompts and common failure modes
- Improve prompt quality for the top three subject/use-case categories
- Refine onboarding copy and dashboard usefulness
- Prepare pitch deck, GitHub polish, and resume bullet

## Analytics Readiness
- Keep analytics light until product direction is validated
- Current implementation target:
  - `module_opened`
  - `generation_started`
  - `generation_completed`
  - `generation_failed`
  - `copy_clicked`
  - `clear_clicked`
  - `retry_clicked`
- Track only module name, success/failure, response length, duration, timestamp, and coarse error category
- Do not add cookies or invasive tracking until a clear need exists
- Prefer explicit environment gating so analytics never block local or production app startup

## Azure Future Scaling Plan
Tauqeer has Azure for Startups access with `$1,000` in credits, but the current MVP should stay on Render + Vercel until user validation proves stronger demand.

- Azure App Service or Azure Container Apps for backend hosting
- Azure Database for PostgreSQL for durable history and user data
- Azure AI Search for syllabus, notes, and retrieval workflows
- Azure Blob Storage for uploaded resources and generated exports
- Azure Monitor / Application Insights for observability
- Azure OpenAI / Azure AI Foundry for enterprise-friendly model routing and governance

## Current Status
- Research, Notes, and Doubt are working with shared SSE streaming
- History works locally with SQLite and is production-ready for PostgreSQL through `DATABASE_URL`
- Frontend is polished enough for demo, recruiter review, and deployment
- Frontend is live on Vercel and backend health is live on Render
- Provider diagnostics, request IDs, rate limiting, and exact/similar cache replay are now part of the production MVP
- Provider resilience now includes:
  - validated-model startup probing
  - strict fallback order
  - Fallback Academic Mode
  - Cached Academic Response mode
  - quota observability
  - provider cooldown behavior
  - no-empty-output guarantee for the three core student modules
- Current production verification shows:
  - Live MVP is stable
  - Gemini provider is degraded due to quota/model access
  - user-facing output remains functional through Fallback Academic Mode
- Current live URLs:
  - Frontend: https://scholr-coral.vercel.app
  - Backend health: https://scholr-k9sj.onrender.com/health

## Pending Work
- Add demo GIF or short walkthrough to the repo
- Gather first real student usage feedback
- Add CI and protected-branch status checks
- Review early analytics signal after the first student validation sprint
- Validate the document intelligence scaffold with real uploaded course PDFs before exposing it in the core UI

## Roadmap Additions

### Auth & security
- Google OAuth login
- user-specific history
- email verification
- protected dashboard
- role-based access later
- rate limiting and abuse protection

### API and data
- keep history pagination simple with `page` and `limit`
- move production persistence to PostgreSQL as usage justifies it
- evaluate whether short-TTL prompt-response caching should stay local, become Redis-backed, or be removed if freshness matters more than quota savings
- add semantic search over saved history only after there is real repeat usage to justify embeddings infrastructure

### Logging and observability
- current MVP direction is structured application logs with request IDs and safe event fields
- centralized logging later with Sentry, Grafana, or Azure Monitor
- stronger uptime and latency tracking after the first usage wave
- add provider scorecards by model if fallback behavior becomes part of ongoing operations
- track quota exhaustion, validated model failures, and provider recovery state as first-class operational signals

### Analytics
- start lightweight with PostHog or Vercel Analytics behind env gating
- avoid invasive tracking or cookies unless truly needed

### SEO and legal
- grow sitemap/search-console coverage as distribution needs increase
- evolve privacy and terms as the product moves beyond MVP

### Future document intelligence lane
- Phase 1: PDF upload and metadata extraction
- Phase 2: chunking and embeddings for notes, slides, and lab manuals
- Phase 3: citations from uploaded files inside Research, Notes, and Doubt
- Phase 4: semantic search across both uploaded material and saved history
- This remains roadmap-only until the current wedge shows repeat usage
