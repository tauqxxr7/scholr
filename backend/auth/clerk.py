"""Verify Clerk session JWT signatures before trusting user identities."""
import os
from functools import lru_cache
from typing import Optional

import jwt
from fastapi import Header
from jwt import PyJWKClient
from jwt.exceptions import PyJWTError

@lru_cache(maxsize=8)
def _jwks_client(jwks_url: str) -> PyJWKClient:
    return PyJWKClient(jwks_url, cache_jwk_set=True, lifespan=300)

async def get_optional_user_id(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Return a verified Clerk subject, or None. Fail closed if not configured."""
    issuer = os.getenv("CLERK_JWT_ISSUER", "").strip().rstrip("/")
    if not issuer or not issuer.startswith("https://"):
        return None
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.removeprefix("Bearer ").strip()
    if not token or len(token) > 8192:
        return None
    try:
        key = _jwks_client(f"{issuer}/.well-known/jwks.json").get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            key.key,
            algorithms=["RS256"],
            issuer=issuer,
            options={"require": ["exp", "iat", "iss", "sub"], "verify_aud": False},
            leeway=30,
        )
        subject = claims.get("sub")
        return subject if isinstance(subject, str) and subject.startswith("user_") else None
    except (PyJWTError, ValueError, TypeError, OSError):
        return None
