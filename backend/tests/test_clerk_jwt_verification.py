import pytest
import jwt
from auth import clerk

@pytest.mark.asyncio
async def test_unsigned_claims_never_become_identity(monkeypatch):
    monkeypatch.setenv("CLERK_JWT_ISSUER", "https://example.clerk.accounts.dev")
    token = jwt.encode({"sub": "user_attacker", "iss": "https://example.clerk.accounts.dev", "exp": 4102444800, "iat": 1700000000}, "attacker-secret", algorithm="HS256")
    assert await clerk.get_optional_user_id(f"Bearer {token}") is None

@pytest.mark.asyncio
async def test_missing_issuer_fails_closed(monkeypatch):
    monkeypatch.delenv("CLERK_JWT_ISSUER", raising=False)
    assert await clerk.get_optional_user_id("Bearer arbitrary") is None
