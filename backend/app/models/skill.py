"""
app/models/skill.py — Shared skill taxonomy.

Skills are a controlled vocabulary — not per-employer.
"Python", "Py", "python3" should all resolve to the same Skill row
via normalization in the service layer (app/services/skill_normalizer.py).
The unique constraint on `name` enforces this at the DB level.
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.employee_skill import EmployeeSkill
    from app.models.project_skill_requirement import ProjectSkillRequirement
    from app.models.verification_test import VerificationTest


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Normalized name — service layer lowercases + title-cases before insert
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    employee_skills: Mapped[list[EmployeeSkill]] = relationship(
        "EmployeeSkill", back_populates="skill"
    )
    project_requirements: Mapped[list[ProjectSkillRequirement]] = relationship(
        "ProjectSkillRequirement", back_populates="skill"
    )
    verification_tests: Mapped[list[VerificationTest]] = relationship(
        "VerificationTest", back_populates="skill"
    )

    def __repr__(self) -> str:
        return f"<Skill id={self.id} name={self.name!r}>"
