"""
app/models/base.py — Declarative base for all SQLAlchemy models.

Every model inherits from Base. Alembic reads Base.metadata to
auto-generate migration scripts.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared base class for all SkillBin ORM models."""
    pass
