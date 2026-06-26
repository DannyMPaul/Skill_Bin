"""
app/models/task_outcome.py — Rating-update trigger record.

When an employer marks a project complete, a TaskOutcome row is written
with the before/after ratings for every required skill. This is the
"match result" that drives the Elo update (IDEA.md §4.4, §5.3).

rating_changes_json schema (list of objects per required skill):
  [
    {
      "skill_id": 1,
      "skill_name": "Python",
      "rating_before": 1375.0,
      "rating_after":  1421.5,
      "rd_before":     262.0,
      "rd_after":      196.5
    },
    ...
  ]

project_id is UNIQUE: one project → at most one outcome.
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, ForeignKey, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.employee import Employee


class OutcomeValue(str, enum.Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAIL = "fail"

    @property
    def numeric(self) -> float:
        """Map to the outcome value used in the Elo formula (IDEA.md §5.3)."""
        return {"success": 1.0, "partial": 0.5, "fail": 0.0}[self.value]


class TaskOutcome(Base):
    __tablename__ = "task_outcomes"

    id: Mapped[int] = mapped_column(primary_key=True)
    # unique=True enforces one outcome per project at the DB level
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    employee_id: Mapped[int] = mapped_column(
        # RESTRICT: keep outcomes for audit even if employee is soft-deleted (Phase 9)
        ForeignKey("employees.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    outcome: Mapped[OutcomeValue] = mapped_column(
        SAEnum(OutcomeValue, native_enum=False, length=10), nullable=False
    )
    quality_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Before/after per-skill ratings — the permanent audit trail
    rating_changes_json: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, nullable=False
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    project: Mapped[Project] = relationship("Project", back_populates="outcome")
    employee: Mapped[Employee] = relationship("Employee", back_populates="outcomes")

    def __repr__(self) -> str:
        return (
            f"<TaskOutcome id={self.id} project_id={self.project_id} "
            f"outcome={self.outcome}>"
        )
