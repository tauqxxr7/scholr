import logging
import os
import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from agents._generation import (
    ensure_provider_recovery_task,
    get_provider_status,
    run_provider_smoke_test,
    shutdown_provider_recovery_task,
    validate_provider_startup,
)
from core.auth import get_auth_context, is_auth_configured, is_auth_enabled, is_auth_required
from core.logging_utils import configure_logging, log_event
from db import crud
from db.database import SessionLocal, init_db
from routers import documents, doubt, history, notes, research
from routers._runtime import get_runtime_diagnostics
from services.document_rag import get_document_intelligence_health

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
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_origin_regex=ALLOWED_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(research.router, prefix="/api", tags=["research"])
app.include_router(notes.router, prefix="/api", tags=["notes"])
app.include_router(doubt.router, prefix="/api", tags=["doubt"])
app.include_router(history.router, prefix="/api", tags=["history"])
app.include_router(documents.router, prefix="/api", tags=["documents"])

logger = logging.getLogger("scholr.api")


@app.on_event("startup")
async def validate_provider_on_startup():
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
        "version": "1.0.0",
        "auth_configured": is_auth_configured(),
        "auth_required": is_auth_required(),
        "auth_enabled": is_auth_enabled(),
        **get_runtime_diagnostics(),
        **provider_status,
    }


@app.get("/health/provider")
def provider_health_check():
    provider_status = get_provider_status()
    return {
        "status": "provider_health",
        **get_runtime_diagnostics(),
        **provider_status,
    }


@app.get("/health/generate-test")
async def provider_generate_test():
    smoke_test = await run_provider_smoke_test()
    return {
        "status": "provider_generate_test",
        **get_runtime_diagnostics(),
        **smoke_test,
    }


@app.get("/health/documents")
def document_intelligence_health():
    return {
        "status": "document_intelligence_health",
        **get_document_intelligence_health(),
    }
