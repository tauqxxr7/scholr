from dataclasses import dataclass
from typing import Any

from fastapi import Request

from db.database import DEFAULT_TENANT_SESSION_ID, DEFAULT_TENANT_USER_ID


@dataclass
class AuthContext:
    user_id: str
    session_id: str
    auth_provider: str
    is_authenticated: bool
    auth_mode: str
    token_claims: dict[str, Any]


def is_auth_configured() -> bool:
    return False


def is_auth_enabled() -> bool:
    return False


def is_auth_required() -> bool:
    return False


def get_auth_context(request: Request, *, allow_unauthenticated: bool = False) -> AuthContext:
    del allow_unauthenticated
    if hasattr(request.state, "auth_context"):
        return request.state.auth_context

    context = AuthContext(
        user_id=DEFAULT_TENANT_USER_ID,
        session_id=DEFAULT_TENANT_SESSION_ID,
        auth_provider="public",
        is_authenticated=False,
        auth_mode="disabled",
        token_claims={},
    )
    request.state.auth_context = context
    return context


def require_auth_context(request: Request) -> AuthContext:
    return get_auth_context(request, allow_unauthenticated=True)
