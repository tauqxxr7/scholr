import os
from dataclasses import dataclass
from typing import Any

from fastapi import HTTPException, Request
try:
    import jwt
    from jwt import PyJWKClient
except ImportError:  # pragma: no cover - depends on environment
    jwt = None
    PyJWKClient = None

from db.database import DEFAULT_TENANT_SESSION_ID, DEFAULT_TENANT_USER_ID

CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL", "https://api.clerk.com/v1/jwks").strip()
CLERK_ISSUER = os.getenv("CLERK_JWT_ISSUER", "").strip()
CLERK_AUDIENCE = os.getenv("CLERK_JWT_AUDIENCE", "").strip()
CLERK_AUTHORIZED_PARTIES = [
    value.strip()
    for value in os.getenv("CLERK_AUTHORIZED_PARTIES", "").split(",")
    if value.strip()
]
AUTH_REQUIRED = os.getenv("AUTH_REQUIRED", "false").strip().lower() in {"1", "true", "yes", "on"}

_JWKS_CLIENT = PyJWKClient(CLERK_JWKS_URL) if CLERK_JWKS_URL and PyJWKClient else None


@dataclass
class AuthContext:
    user_id: str
    session_id: str
    auth_provider: str
    is_authenticated: bool
    auth_mode: str
    token_claims: dict[str, Any]


def is_auth_configured() -> bool:
    return bool(
        CLERK_JWKS_URL
        and (
            AUTH_REQUIRED
            or CLERK_ISSUER
            or CLERK_AUDIENCE
            or CLERK_AUTHORIZED_PARTIES
        )
    )


def is_auth_enabled() -> bool:
    return AUTH_REQUIRED or is_auth_configured()


def is_auth_required() -> bool:
    return AUTH_REQUIRED


def _get_bearer_token(request: Request) -> str | None:
    authorization = request.headers.get("authorization", "").strip()
    if authorization.lower().startswith("bearer "):
        return authorization[7:].strip()
    return None


def _verify_clerk_token(token: str) -> dict[str, Any]:
    if jwt is None or PyJWKClient is None or _JWKS_CLIENT is None:
        raise HTTPException(status_code=503, detail="Clerk JWKS client is not configured.")

    signing_key = _JWKS_CLIENT.get_signing_key_from_jwt(token)
    decode_kwargs: dict[str, Any] = {
        "algorithms": ["RS256"],
        "options": {"require": ["exp", "iat", "nbf", "sub", "sid"]},
    }
    if CLERK_AUDIENCE:
        decode_kwargs["audience"] = CLERK_AUDIENCE
    else:
        decode_kwargs["options"]["verify_aud"] = False
    if CLERK_ISSUER:
        decode_kwargs["issuer"] = CLERK_ISSUER

    claims = jwt.decode(token, signing_key.key, **decode_kwargs)
    if CLERK_AUTHORIZED_PARTIES:
        azp = claims.get("azp")
        if azp not in CLERK_AUTHORIZED_PARTIES:
            raise HTTPException(status_code=401, detail="Authorized party is not allowed for this backend.")
    return claims


def get_auth_context(request: Request, *, allow_unauthenticated: bool = False) -> AuthContext:
    if hasattr(request.state, "auth_context"):
        return request.state.auth_context

    token = _get_bearer_token(request)
    if not token:
        if AUTH_REQUIRED and not allow_unauthenticated:
            raise HTTPException(status_code=401, detail="Authentication is required.")
        context = AuthContext(
            user_id=DEFAULT_TENANT_USER_ID,
            session_id=DEFAULT_TENANT_SESSION_ID,
            auth_provider="demo",
            is_authenticated=False,
            auth_mode="disabled",
            token_claims={},
        )
        request.state.auth_context = context
        return context

    try:
        claims = _verify_clerk_token(token)
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - depends on runtime token/JWKS state
        raise HTTPException(status_code=401, detail="Session token could not be verified.") from exc

    context = AuthContext(
        user_id=str(claims["sub"]),
        session_id=str(claims.get("sid", DEFAULT_TENANT_SESSION_ID)),
        auth_provider="clerk",
        is_authenticated=True,
        auth_mode="required" if AUTH_REQUIRED else "optional",
        token_claims=claims,
    )
    request.state.auth_context = context
    return context


def require_auth_context(request: Request) -> AuthContext:
    context = get_auth_context(request, allow_unauthenticated=False)
    if AUTH_REQUIRED and not context.is_authenticated:
        raise HTTPException(status_code=401, detail="Authentication is required.")
    return context
