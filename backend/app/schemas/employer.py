"""
app/schemas/employer.py — Pydantic request/response models for auth.

All user input is validated here server-side (CLAUDE.md requirement).
Passwords are validated for minimum length — never logged or returned.
"""
from datetime import datetime

from pydantic import BaseModel, EmailStr, field_validator


# ── Request bodies ─────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_strong_enough(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ── Response bodies ────────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int          # seconds — convenience for frontend token refresh logic


class EmployerOut(BaseModel):
    """Safe employer representation — never includes password_hash."""
    id: int
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}
