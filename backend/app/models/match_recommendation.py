"""
app/models/match_recommendation.py — Audit trail for matching decisions.

Every time "the Bin" is invoked, a row is saved here with:
  - The full ranked candidate list (fit scores, per-skill breakdown, workload)
  - Which employee the employer ultimately chose
  - Whether the employer overrode the top recommendation

This is the explainability / audit log that lets an employer trace
any assignment decision back to exactly what the system suggested.

candidates_json schema (list of objects):
  [
    {
      "employee_id": 42,
      "fit_score": 0.73,
      "per_skill_breakdown": [{"skill_id": 1, "skill_name": "Python", "employee_rating": 1375, "difficulty": 1600, "p_success": 0.62}],
      "workload_at_time": 1,
      "excluded_reason": null
    },
    ...
  ]
"""
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.employee import Employee


class MatchRecommendation(Base):
    __tablename__ = "match_recommendations"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    # Full ranked candidate list — JSONB for PostgreSQL (supports indexing + operators)
    candidates_json: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, nullable=False
    )
    # Which employee was actually assigned (null until employer acts)
    chosen_employee_id: Mapped[int | None] = mapped_column(
        ForeignKey("employees.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # True when the employer picked someone other than the top recommendation
    employer_override: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # ── Relationships ─────────────────────────────────────────────────────────
    project: Mapped[Project] = relationship(
        "Project", back_populates="match_recommendations"
    )
    chosen_employee: Mapped[Employee | None] = relationship(
        "Employee", foreign_keys=[chosen_employee_id]
    )

    def __repr__(self) -> str:
        return (
            f"<MatchRecommendation id={self.id} project_id={self.project_id} "
            f"override={self.employer_override}>"
        )
