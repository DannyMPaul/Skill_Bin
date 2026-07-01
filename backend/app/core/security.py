"""
app/core/security.py — Password hashing and JWT helpers.

Security rules (CLAUDE.md):
- Passwords are ONLY hashed here — never stored, logged, or returned in plain.
- JWT secret is read from settings — never hardcoded.
- decode_access_token raises JWTError on ANY validation failure so the caller
  can return a generic 401 without leaking which field was bad.
"""
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt  # python-jose
from passlib.context import CryptContext

from app.core.config import settings

# bcrypt is the scheme — argon2 can be added later as an upgrade path
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Password helpers ───────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    """Return a bcrypt hash of `plain`. Never call with an already-hashed value."""
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Constant-time comparison via passlib.
    Returns False (not raises) when the password is wrong so callers can
    produce an identical response for wrong-email and wrong-password cases.
    """
    return pwd_context.verify(plain, hashed)


# ── JWT helpers ────────────────────────────────────────────────────────────────

def create_access_token(employer_id: int) -> str:
    """Mint a signed JWT. Subject is the employer's integer PK as a string."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload = {
        "sub": str(employer_id),
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> int:
    """
    Validate signature + expiry, return employer_id.
    Raises JWTError on any failure — caller should return 401.
    """
    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
    )
    sub: str | None = payload.get("sub")
    if not sub:
        raise JWTError("Token missing 'sub' claim")
    return int(sub)
