"""
app/core/deps.py — Reusable FastAPI dependencies.

get_current_employer is the auth guard used on every protected route.
Import and add it as a Depends() on any route that requires a logged-in employer.

Usage in a route handler:
    employer: Employer = Depends(get_current_employer)
"""
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db import get_db
from app.models import Employer

logger = logging.getLogger(__name__)

# auto_error=False → we return our own 401 instead of the default 403
_http_bearer = HTTPBearer(auto_error=False)

_UNAUTHORIZED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Authentication required",
    headers={"WWW-Authenticate": "Bearer"},
)

_INVALID_TOKEN = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid or expired token",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_employer(
    credentials: HTTPAuthorizationCredentials | None = Depends(_http_bearer),
    db: Session = Depends(get_db),
) -> Employer:
    """
    Extract + validate the Bearer JWT, return the owning Employer row.

    Raises 401 on any failure with a generic message — never reveals
    whether the token was missing, expired, or from a deleted employer.
    """
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _UNAUTHORIZED

    try:
        employer_id = decode_access_token(credentials.credentials)
    except (JWTError, ValueError):
        raise _INVALID_TOKEN

    employer = db.query(Employer).filter(Employer.id == employer_id).first()
    if employer is None:
        # Token was valid but the employer account no longer exists
        logger.warning("Valid JWT for non-existent employer_id=%s", employer_id)
        raise _INVALID_TOKEN

    return employer
