"""
app/models/__init__.py

Import every model here so that:
  1. Alembic's env.py picks them all up via Base.metadata when it runs
     `from app.models import *` (or just `import app.models`).
  2. Callers can do `from app.models import Employer, Employee, ...`
     without knowing the individual module layout.

Add new model imports here as phases introduce new tables.
"""
from app.models.base import Base  # noqa: F401

# ── All ORM models (Phase 1) ──────────────────────────────────────────────────
from app.models.employer import Employer  # noqa: F401
from app.models.employee import Employee  # noqa: F401
from app.models.skill import Skill  # noqa: F401
from app.models.employee_skill import EmployeeSkill, SkillSource  # noqa: F401
from app.models.project import Project, ProjectStatus  # noqa: F401
from app.models.project_skill_requirement import ProjectSkillRequirement  # noqa: F401
from app.models.match_recommendation import MatchRecommendation  # noqa: F401
from app.models.task_outcome import TaskOutcome, OutcomeValue  # noqa: F401
from app.models.verification_test import VerificationTest  # noqa: F401

__all__ = [
    "Base",
    "Employer",
    "Employee",
    "Skill",
    "EmployeeSkill",
    "SkillSource",
    "Project",
    "ProjectStatus",
    "ProjectSkillRequirement",
    "MatchRecommendation",
    "TaskOutcome",
    "OutcomeValue",
    "VerificationTest",
]
