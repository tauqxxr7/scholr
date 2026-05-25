from datetime import datetime
import platform
import sys

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from db.database import Feedback, SearchHistory, get_db

router = APIRouter()


@router.get("/api/evidence")
def get_technical_evidence(db: Session = Depends(get_db)):
    """
    Technical evidence package for Microsoft for Startups application.
    Documents that Scholr is a real production AI system.
    """
    now = datetime.utcnow()

    total_searches = db.query(func.count(SearchHistory.id)).scalar() or 0
    total_feedback = db.query(func.count(Feedback.id)).scalar() or 0
    helpful = db.query(func.count(Feedback.id)).filter(
        Feedback.rating == "helpful"
    ).scalar() or 0

    by_module = db.query(
        SearchHistory.module,
        func.count(SearchHistory.id).label("count")
    ).group_by(SearchHistory.module).all()

    return {
        "product": {
            "name": "Scholr",
            "description": "AI-powered academic platform for BTech students",
            "founder": "Tauqeer Bharde",
            "stage": "Live MVP",
            "target_market": "10M+ BTech engineering students in India",
        },
        "live_surfaces": {
            "frontend": "https://scholr-coral.vercel.app",
            "backend": "https://scholr-k9sj.onrender.com",
            "health": "https://scholr-k9sj.onrender.com/health",
            "routes": "https://scholr-k9sj.onrender.com/health/routes",
        },
        "tech_stack": {
            "frontend": "Next.js 14, TypeScript, Tailwind CSS, shadcn/ui",
            "backend": "Python FastAPI, SQLAlchemy, SSE streaming",
            "ai_layer": "OpenRouter with google/gemini-2.0-flash-lite-001, fallback engine",
            "database": "SQLite local, PostgreSQL-ready via DATABASE_URL",
            "hosting": "Vercel (frontend) + Render (backend)",
            "ci_cd": "GitHub Actions - backend CI + frontend CI + repo hygiene",
        },
        "engineering_features": [
            "Real-time SSE streaming with 5s first-token timeout and 20s hard cutoff",
            "Multi-provider resilience with automatic fallback academic engine",
            "In-memory response cache with TTL and LRU eviction",
            "Per-IP rate limiting via slowapi (20 req/min AI endpoints)",
            "Structured response logging with first-token and completion timing",
            "Output section validation with logging for AI quality monitoring",
            "PDF export of all AI responses with Scholr branding",
            "PostHog analytics integration for usage tracking",
            "Sentry error monitoring on FastAPI backend",
            "Clerk authentication scaffold with optional JWT user tagging",
            "Sitemap.xml and robots.txt for SEO",
            "19 backend unit tests with pytest, CI green on every push",
        ],
        "production_stats": {
            "total_ai_queries": total_searches,
            "total_feedback_submitted": total_feedback,
            "helpful_responses": helpful,
            "helpful_rate_percent": round(helpful / total_feedback * 100, 1) if total_feedback > 0 else None,
            "modules_used": {row.module: row.count for row in by_module},
            "evidence_generated_at": now.isoformat(),
        },
        "azure_integration_plan": {
            "phase_1": "Azure OpenAI as additional provider fallback alongside OpenRouter",
            "phase_2": "Azure Cognitive Search for semantic search across student history",
            "phase_3": "Azure Cosmos DB for scalable multi-region student data",
            "phase_4": "Azure Functions for async PDF processing and batch note generation",
            "reason": "Current architecture is provider-agnostic by design, making Azure integration straightforward",
        },
        "runtime": {
            "python_version": sys.version,
            "platform": platform.system(),
            "evidence_endpoint_version": "1.0.0",
        },
    }
