# Scholr - Microsoft for Startups Application Support

**Founder:** Tauqeer Bharde  
**Email:** tauqeerplayer@gmail.com  
**LinkedIn:** https://www.linkedin.com/in/tauqeer-sameer-85b868235  
**Product:** https://scholr-coral.vercel.app  
**GitHub:** https://github.com/tauqxxr7/scholr

## What Scholr Is

Scholr is a live AI-powered academic platform for BTech engineering students in India. Students get research paper recommendations, structured study notes, and doubt solving through a streaming AI interface - free, no signup required.

## Why Microsoft

We are applying to Microsoft for Startups to:
1. Access Azure OpenAI as a primary AI provider alongside OpenRouter
2. Use Azure Cognitive Search for semantic retrieval over student history
3. Deploy on Azure App Service for Indian-region low-latency hosting
4. Access Azure AI Studio for fine-tuning on engineering academic content

## Current Technical State

- Frontend: Next.js 14 + TypeScript, live on Vercel
- Backend: Python FastAPI, live on Render
- Current version: 1.6.0
- AI: OpenRouter (google/gemini-2.0-flash-lite-001) with fallback engine
- Database: SQLite with PostgreSQL-ready architecture
- Tests: 35 backend unit tests, CI green on every push
- API endpoints: 15+ registered, all returning 200
- Evidence endpoint: https://scholr-k9sj.onrender.com/api/evidence

## Azure Integration Roadmap

### Phase 1 (Month 1 with Azure credits)
- Add Azure OpenAI as provider in the existing multi-provider architecture
- No code restructure needed - provider layer already abstracted

### Phase 2 (Month 2)
- Azure Cognitive Search for semantic search over student history
- Replace current TF-IDF embeddings with Azure embeddings

### Phase 3 (Month 3)
- Azure Cosmos DB for scalable multi-user data
- Azure Functions for async PDF processing

## Market

- 10M+ BTech engineering students in India
- No affordable India-first AI academic tool exists
- Global EdTech AI market: $400B by 2030

## Traction

- Live product with real deployments
- AI module latency: <2s first token, <5s completion
- Mobile verified on iOS and Android viewports
- Microsoft for Startups application submitted
