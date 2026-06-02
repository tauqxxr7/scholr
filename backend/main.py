import logging
import os
import uuid

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.requests import Request

from agents._generation import (
    ensure_provider_recovery_task,
    get_provider_status,
    shutdown_provider_recovery_task,
    validate_provider_startup,
)
from core.auth import get_auth_context
from core.logging_utils import configure_logging, log_event
from core.slowapi_limiter import limiter
from db import crud
from db.database import SessionLocal, init_db
from routers import documents, doubt, evidence, feedback, feedback_form, history, linkedin, metrics, notes, research, search, stats, status, validation, waitlist
from routers._runtime import get_runtime_diagnostics
from services.document_rag import get_document_intelligence_health
from telemetry import get_all as get_telemetry_counters

sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[FastApiIntegration(), SqlalchemyIntegration()],
        traces_sample_rate=0.1,
        environment=os.getenv("ENVIRONMENT", "production"),
    )

configure_logging()
init_db()


def _parse_allowed_origins() -> list[str]:
    defaults = {
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://scholr-coral.vercel.app",
    }

    configured = os.getenv("ALLOWED_ORIGINS", "")
    if configured:
        defaults.update(
            origin.strip()
            for origin in configured.split(",")
            if origin.strip()
        )

    vercel_url = os.getenv("VERCEL_URL", "").strip()
    if vercel_url:
        if vercel_url.startswith("http://") or vercel_url.startswith("https://"):
            defaults.add(vercel_url.rstrip("/"))
        else:
            defaults.add(f"https://{vercel_url.rstrip('/')}")

    frontend_url = os.getenv("FRONTEND_URL", "").strip()
    if frontend_url:
        defaults.add(frontend_url.rstrip("/"))

    return sorted(defaults)


ALLOWED_ORIGINS = _parse_allowed_origins()
ALLOWED_ORIGIN_REGEX = os.getenv("ALLOWED_ORIGIN_REGEX", r"https://.*\.vercel\.app")

app = FastAPI(
    title="Scholr API",
    description="AI Academic Platform for BTech Students",
    version=os.getenv("APP_VERSION", "1.6.0"),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=ALLOWED_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(research.router, prefix="/api", tags=["research"])
app.include_router(notes.router, prefix="/api", tags=["notes"])
app.include_router(doubt.router, prefix="/api", tags=["doubt"])
app.include_router(history.router, prefix="/api", tags=["history"])
app.include_router(documents.router, prefix="/api", tags=["documents"])
app.include_router(feedback.router, prefix="/api", tags=["feedback"])
app.include_router(feedback_form.router, tags=["feedback-form"])
app.include_router(metrics.router, tags=["metrics"])
app.include_router(waitlist.router, tags=["waitlist"])
app.include_router(validation.router, tags=["validation"])
app.include_router(evidence.router, tags=["evidence"])
app.include_router(linkedin.router, tags=["linkedin"])
app.include_router(search.router, tags=["search"])
app.include_router(stats.router, tags=["stats"])
app.include_router(status.router, tags=["status"])

logger = logging.getLogger("scholr.api")


@app.on_event("startup")
async def validate_provider_on_startup():
    version = os.getenv("APP_VERSION", "1.6.0")
    logger.info("Scholr API starting - version %s", version)
    logger.info("Environment: %s", os.getenv("ENVIRONMENT", "production"))
    logger.info("Database: %s...", os.getenv("DATABASE_URL", "sqlite")[:20])
    logger.info("Sentry: %s", "configured" if os.getenv("SENTRY_DSN") else "not configured")
    logger.info(
        "OpenRouter: %s",
        "configured" if os.getenv("OPENROUTER_API_KEY") else "NOT CONFIGURED - AI will use fallback",
    )
    logger.info("Gemini: %s", "configured" if os.getenv("GEMINI_API_KEY") else "not configured")
    if not os.getenv("OPENROUTER_API_KEY") and not os.getenv("GEMINI_API_KEY"):
        logger.warning("=" * 60)
        logger.warning("WARNING: No AI provider key configured.")
        logger.warning("OPENROUTER_API_KEY and GEMINI_API_KEY are both missing.")
        logger.warning("All requests will use the fallback academic engine.")
        logger.warning("Set OPENROUTER_API_KEY in Render Environment to enable real AI.")
        logger.warning("=" * 60)
    elif os.getenv("OPENROUTER_API_KEY"):
        logger.info("OpenRouter key: configured")
    elif os.getenv("GEMINI_API_KEY"):
        logger.info("Gemini key: configured")

    ensure_provider_recovery_task()
    provider_status = await validate_provider_startup()

    log_event(
        logger,
        "provider_startup_validation",
        provider_configured=provider_status["provider_configured"],
        provider_ready=provider_status["provider_ready"],
        active_provider=provider_status["active_provider"],
        fallback_provider=provider_status["fallback_provider"],
        provider_failover_reason=provider_status["provider_failover_reason"],
        model_name=provider_status["model_name"],
        selected_model=provider_status["selected_model"],
        candidate_models_count=provider_status["candidate_models_count"],
        rejected_models_count=provider_status["rejected_models_count"],
        validated_models_count=provider_status["validated_models_count"],
        failed_validation_models_count=provider_status["failed_validation_models_count"],
        selected_model_validation_status=provider_status["selected_model_validation_status"],
        model_selection_strategy=provider_status["model_selection_strategy"],
        error_category=provider_status["provider_error_category"],
    )

    if not provider_status["provider_ready"]:
        log_event(
            logger,
            "GEMINI_PROVIDER_NOT_READY",
            provider_configured=provider_status["provider_configured"],
            active_provider=provider_status["active_provider"],
            fallback_provider=provider_status["fallback_provider"],
            provider_failover_reason=provider_status["provider_failover_reason"],
            model_name=provider_status["model_name"],
            selected_model=provider_status["selected_model"],
            candidate_models_count=provider_status["candidate_models_count"],
            rejected_models_count=provider_status["rejected_models_count"],
            validated_models_count=provider_status["validated_models_count"],
            failed_validation_models_count=provider_status["failed_validation_models_count"],
            selected_model_validation_status=provider_status["selected_model_validation_status"],
            model_selection_strategy=provider_status["model_selection_strategy"],
            error_category=provider_status["provider_error_category"],
        )


@app.on_event("shutdown")
async def stop_provider_recovery_task():
    await shutdown_provider_recovery_task()


@app.middleware("http")
async def add_request_context(request: Request, call_next):
    request_id = request.headers.get("x-request-id", "").strip() or str(uuid.uuid4())
    request.state.request_id = request_id

    client_ip = "unknown"
    if request.client and request.client.host:
        client_ip = request.client.host

    log_event(
        logger,
        "request_started",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        client_ip=client_ip,
    )

    auth_context = get_auth_context(request, allow_unauthenticated=True)
    db = SessionLocal()
    try:
        crud.upsert_user_session(
            db,
            user_id=auth_context.user_id,
            session_id=auth_context.session_id,
            auth_provider=auth_context.auth_provider,
            user_agent=request.headers.get("user-agent"),
        )
    finally:
        db.close()
    log_event(
        logger,
        "request_authenticated",
        request_id=request_id,
        user_id=auth_context.user_id,
        session_id=auth_context.session_id,
        is_authenticated=auth_context.is_authenticated,
        auth_mode=auth_context.auth_mode,
    )

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/health")
def health_check():
    provider_status = get_provider_status()
    return {
        "status": "Scholr API is running",
        "version": os.getenv("APP_VERSION", "1.6.0"),
        **get_runtime_diagnostics(),
        **provider_status,
        **get_telemetry_counters(),
        "telemetry": get_telemetry_counters(),
    }


@app.get("/ping")
def ping():
    return {"ok": True}


@app.get("/health/provider")
def provider_health_check():
    provider_status = get_provider_status()
    return {
        "status": "provider_health",
        **get_runtime_diagnostics(),
        **provider_status,
    }


@app.get("/health/routes")
def list_routes():
    routes = []
    for route in app.routes:
        if hasattr(route, "path") and hasattr(route, "methods"):
            routes.append(
                {
                    "path": route.path,
                    "methods": list(route.methods) if route.methods else [],
                }
            )
    return {
        "total_routes": len(routes),
        "routes": sorted(routes, key=lambda r: r["path"]),
        "version": os.getenv("APP_VERSION", "1.6.0"),
    }


@app.get("/health/generate-test")
@app.get("/api/health/generate-test")
async def test_generation():
    try:
        from agents.research_agent import generate_research_response

        chunks = []
        async for chunk in generate_research_response("binary search"):
            chunks.append(chunk)
        text = "".join(chunks)
        return {
            "ai_working": len(text) > 50,
            "chars_received": len(text),
            "preview": text[:100],
            "provider": "live",
        }
    except Exception as exc:
        return {"ai_working": False, "error": str(exc)}


@app.get("/health/documents")
def document_intelligence_health():
    return {
        "status": "document_intelligence_health",
        **get_document_intelligence_health(),
    }
