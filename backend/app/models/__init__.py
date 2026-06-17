"""
app/models/__init__.py

Import all models here so Alembic's env.py picks them up via Base.metadata
when it imports this package. Add new model imports as phases progress.
"""
from app.models.base import Base  # noqa: F401 — must be importable

# Phase 1 will add:
# from app.models.employer import Employer       # noqa: F401
# from app.models.employee import Employee       # noqa: F401
# from app.models.skill import Skill             # noqa: F401
# ... etc.

__all__ = ["Base"]
