"""
app/models/employee.py — Employee profile object.

In v1, employees are NOT real user accounts. They are profile records
created and managed entirely by the employer. The employer enters
their resume; the system extracts skills and builds ratings from it.

current_load is DERIVED (not stored) — computed from assigned_projects
at runtime. The matching service uses a SQL subquery for efficiency;
the Python property here is for convenience in tests and small queries.

employer_id is added for multi-tenancy readiness (Phase 5 security note):
  "Write queries so they'd still hold under multi-tenancy later."
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.employer import Employer
    from app.models.employee_skill import EmployeeSkill
    from app.models.project import Project, ProjectStatus
    from app.models.task_outcome import TaskOutcome
    from app.models.verification_test import VerificationTest


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    employer_id: Mapped[int] = mapped_column(
        ForeignKey("employers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # Raw resume text capped by the API layer before storage (CLAUDE.md)
    raw_resume_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Max concurrent active tasks — default 3 per IDEA.md §3
    capacity: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    employer: Mapped[Employer] = relationship("Employer", back_populates="employees")
    skills: Mapped[list[EmployeeSkill]] = relationship(
        "EmployeeSkill", back_populates="employee", cascade="all, delete-orphan"
    )
    assigned_projects: Mapped[list[Project]] = relationship(
        "Project",
        back_populates="assigned_employee",
        foreign_keys="Project.assigned_employee_id",
    )
    outcomes: Mapped[list[TaskOutcome]] = relationship(
        "TaskOutcome", back_populates="employee"
    )
    verification_tests: Mapped[list[VerificationTest]] = relationship(
        "VerificationTest", back_populates="employee", cascade="all, delete-orphan"
    )

    # ── Derived properties (not stored in DB) ─────────────────────────────────

    @property
    def current_load(self) -> int:
        """
        Count of active (assigned or in_progress) tasks.

        WARNING: accessing this triggers a lazy-load of assigned_projects.
        In the matching service use a SQL subquery instead of iterating here.
        """
        from app.models.project import ProjectStatus

        return sum(
            1
            for p in self.assigned_projects
            if p.status in (ProjectStatus.ASSIGNED, ProjectStatus.IN_PROGRESS)
        )

    @property
    def is_available(self) -> bool:
        """True when the employee has room for at least one more task."""
        return self.current_load < self.capacity

    def __repr__(self) -> str:
        return f"<Employee id={self.id} name={self.name!r}>"
