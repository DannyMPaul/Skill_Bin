"""
app/models/project.py — Task / project record.

Status transitions (enforced at the service layer, not the DB):
  unassigned → assigned → in_progress → completed

employer_id included for multi-tenancy readiness (same rationale as Employee).
assigned_employee_id becomes non-null when status moves to 'assigned'.
completed_at is set when status moves to 'completed'.
"""
from __future__ import annotations

import enum
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.employer import Employer
    from app.models.employee import Employee
    from app.models.project_skill_requirement import ProjectSkillRequirement
    from app.models.match_recommendation import MatchRecommendation
    from app.models.task_outcome import TaskOutcome


class ProjectStatus(str, enum.Enum):
    UNASSIGNED = "unassigned"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    employer_id: Mapped[int] = mapped_column(
        ForeignKey("employers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # native_enum=False → VARCHAR + CHECK constraint, easier to extend in migrations
    status: Mapped[ProjectStatus] = mapped_column(
        SAEnum(ProjectStatus, native_enum=False, length=15),
        default=ProjectStatus.UNASSIGNED,
        nullable=False,
    )
    assigned_employee_id: Mapped[int | None] = mapped_column(
        ForeignKey("employees.id", ondelete="SET NULL"), nullable=True, index=True
    )
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    employer: Mapped[Employer] = relationship("Employer", back_populates="projects")
    assigned_employee: Mapped[Employee | None] = relationship(
        "Employee",
        back_populates="assigned_projects",
        foreign_keys=[assigned_employee_id],
    )
    skill_requirements: Mapped[list[ProjectSkillRequirement]] = relationship(
        "ProjectSkillRequirement",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    match_recommendations: Mapped[list[MatchRecommendation]] = relationship(
        "MatchRecommendation",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    # One project has at most one outcome (uselist=False)
    outcome: Mapped[TaskOutcome | None] = relationship(
        "TaskOutcome", back_populates="project", uselist=False
    )

    def __repr__(self) -> str:
        return f"<Project id={self.id} title={self.title!r} status={self.status}>"
