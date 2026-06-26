"""
app/models/employee_skill.py — Per-employee skill rating record.

This is the core data record of the rating system (IDEA.md §3, §5.2, §5.3).
One row per (employee, skill) pair — the unique constraint enforces this.

Rating fields:
  rating          — Elo-style numeric rating, seeded at ~1000
  rating_deviation — Confidence measure (high = uncertain; starts at 350 for resume seeds)
  source          — How this rating was established
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, UniqueConstraint
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.skill import Skill


class SkillSource(str, enum.Enum):
    RESUME_SEED = "resume_seed"
    TASK_OUTCOME = "task_outcome"
    VERIFICATION_TEST = "verification_test"


class EmployeeSkill(Base):
    __tablename__ = "employee_skills"
    __table_args__ = (
        UniqueConstraint("employee_id", "skill_id", name="uq_employee_skill"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True
    )
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # Elo-style rating — default seed 1000 per IDEA.md §5.2
    rating: Mapped[float] = mapped_column(Float, default=1000.0, nullable=False)
    # Confidence: 350 = resume-only (high uncertainty), shrinks toward 50 with outcomes
    rating_deviation: Mapped[float] = mapped_column(Float, default=350.0, nullable=False)
    source: Mapped[SkillSource] = mapped_column(
        SAEnum(SkillSource, native_enum=False, length=20),
        default=SkillSource.RESUME_SEED,
        nullable=False,
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    employee: Mapped[Employee] = relationship("Employee", back_populates="skills")
    skill: Mapped[Skill] = relationship("Skill", back_populates="employee_skills")

    def __repr__(self) -> str:
        return (
            f"<EmployeeSkill employee_id={self.employee_id} "
            f"skill={self.skill_id} rating={self.rating:.0f} RD={self.rating_deviation:.0f}>"
        )
