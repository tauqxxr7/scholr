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
- Recommended first internal events:
  - `landing_cta_clicked`
  - `module_opened`
  - `generation_started`
  - `generation_completed`
  - `generation_failed`
  - `history_viewed`
- Do not add cookies or invasive tracking until a clear need exists
- If analytics are added later, prefer privacy-friendly product analytics with explicit environment gating

## Azure Future Scaling Plan
- Azure OpenAI or Azure AI Studio for enterprise-friendly model routing and governance
- Azure Functions for async and scheduled background workloads
- Azure Cosmos DB for globally distributed user and history storage
- Azure AI Search for syllabus, notes, and retrieval workflows
- Azure Blob Storage for uploaded resources and generated exports
- Azure API Management for rate limiting, partner access, and observability

## Current Status
- Research, Notes, and Doubt are working with shared SSE streaming
- History works locally with SQLite and is production-ready for PostgreSQL through `DATABASE_URL`
- Frontend is polished enough for demo, recruiter review, and deployment
- Frontend is live on Vercel and backend health is live on Render
- Production smoke test has passed for landing, research, notes, doubt, and `/health`

## Pending Work
- Add demo GIF or short walkthrough to the repo
- Gather first real student usage feedback
- Add CI and protected-branch status checks

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

### Logging and observability
- centralized logging later with Sentry, Grafana, or Azure Monitor
- stronger uptime and latency tracking after the first usage wave

### Analytics
- start lightweight with Vercel Analytics or PostHog later
- avoid invasive tracking or cookies unless truly needed

### SEO and legal
- grow sitemap/search-console coverage as distribution needs increase
- evolve privacy and terms as the product moves beyond MVP
