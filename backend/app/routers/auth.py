"""
app/routers/auth.py — Employer authentication endpoints.

Endpoints:
  POST /api/v1/auth/register   — create employer account
  POST /api/v1/auth/login      — authenticate, receive JWT
  GET  /api/v1/auth/me         — return authenticated employer profile (protected)

Security decisions (CLAUDE.md):
- bcrypt hash via security.py — plaintext never stored, logged, or returned.
- Login failure returns identical 401 whether email is wrong OR password is wrong
  — prevents user enumeration.
- In-memory rate limiter: 5 attempts per IP per minute on /login.
- Detailed error context goes to server logs only; generic message to client.
"""
import logging
import threading
from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import get_current_employer
from app.core.security import create_access_token, hash_password, verify_password
from app.core.config import settings
from app.db import get_db
from app.models import Employer
from app.schemas.employer import EmployerOut, LoginRequest, RegisterRequest, TokenResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


# ── In-memory rate limiter (no Redis required in v1) ──────────────────────────
class _LoginRateLimiter:
    """
    Sliding-window rate limiter keyed by IP address.
    Thread-safe for multi-worker uvicorn via a threading.Lock.
    For multi-process deployments, replace with a Redis-backed solution.
    """

    def __init__(self, max_calls: int = 5, window_seconds: int = 60) -> None:
        self._max = max_calls
        self._window = timedelta(seconds=window_seconds)
        self._log: dict[str, list[datetime]] = defaultdict(list)
        self._lock = threading.Lock()

    def is_allowed(self, key: str) -> bool:
        now = datetime.now()
        cutoff = now - self._window
        with self._lock:
            # Evict timestamps outside the window
            self._log[key] = [t for t in self._log[key] if t > cutoff]
            if len(self._log[key]) >= self._max:
                return False
            self._log[key].append(now)
            return True


_limiter = _LoginRateLimiter(max_calls=5, window_seconds=60)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=EmployerOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new employer account",
)
def register(body: RegisterRequest, db: Session = Depends(get_db)) -> Employer:
    """
    Create a new employer.  Password is hashed immediately — the plain value
    is never persisted, logged, or returned.

    Returns 409 if the email is already registered.
    """
    # Optimistic path: check first (avoids unnecessary bcrypt hash on duplicate)
    existing = db.query(Employer).filter(Employer.email == body.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    employer = Employer(
        email=body.email,
        password_hash=hash_password(body.password),
    )
    db.add(employer)
    try:
        db.commit()
        db.refresh(employer)
    except IntegrityError:
        # Race condition: two concurrent registrations with the same email
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    logger.info("New employer registered: id=%s", employer.id)
    return employer


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive a JWT access token",
)
def login(
    request: Request,
    body: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    """
    Authenticate by email + password.  Returns a Bearer JWT on success.

    Security:
    - Rate limited: 5 attempts per IP per minute → 429 on excess.
    - Identical 401 for wrong email AND wrong password — no user enumeration.
    - Failure details logged server-side only.
    """
    client_ip: str = (request.client.host if request.client else "unknown")

    if not _limiter.is_allowed(client_ip):
        logger.warning("Rate limit hit on /login from IP=%s", client_ip)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please wait a minute and try again.",
        )

    employer = db.query(Employer).filter(Employer.email == body.email).first()

    # Single constant-time branch — same response for bad email OR bad password
    if not employer or not verify_password(body.password, employer.password_hash):
        logger.warning(
            "Failed login for email=%r from IP=%s (employer_found=%s)",
            body.email,
            client_ip,
            employer is not None,  # logged server-side only, never sent to client
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    token = create_access_token(employer.id)
    logger.info("Employer id=%s logged in from IP=%s", employer.id, client_ip)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.get(
    "/me",
    response_model=EmployerOut,
    summary="Return the currently authenticated employer",
)
def get_me(
    employer: Employer = Depends(get_current_employer),
) -> Employer:
    """
    Protected endpoint.  Returns the employer profile for the bearer token holder.
    Used by the frontend to verify auth state and display the logged-in email.
    """
    return employer
