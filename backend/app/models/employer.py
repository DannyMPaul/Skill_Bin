"""
app/models/employer.py — Employer ORM model.

The Employer is the only real authenticated user in v1.
They manage employees (as profile objects) and create/assign projects.
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.project import Project


class Employer(Base):
    __tablename__ = "employers"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(254), unique=True, nullable=False, index=True
    )
    # bcrypt / argon2 hash — plaintext password is NEVER stored
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    employees: Mapped[list[Employee]] = relationship(
        "Employee", back_populates="employer", cascade="all, delete-orphan"
    )
    projects: Mapped[list[Project]] = relationship(
        "Project", back_populates="employer", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Employer id={self.id} email={self.email!r}>"
