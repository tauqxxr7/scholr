from typing import Optional
from fastapi import Header


async def get_optional_user_id(authorization: Optional[str] = Header(None)) -> Optional[str]:
    """Extract user_id from Clerk JWT if present. Returns None for unauthenticated requests."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    try:
        import jwt
        token = authorization.split(" ")[1]
        decoded = jwt.decode(token, options={"verify_signature": False})
        return decoded.get("sub")
    except Exception:
        return None
