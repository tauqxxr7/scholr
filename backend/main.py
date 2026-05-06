import logging
import os
import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

from core.logging_utils import configure_logging, log_event
from db.database import init_db
from routers import doubt, history, notes, research

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

logger = logging.getLogger("scholr.api")


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

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/health")
def health_check():
    return {"status": "Scholr API is running", "version": "1.0.0"}
