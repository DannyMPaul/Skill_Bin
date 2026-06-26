"""
app/models/project_skill_requirement.py — Required skills per project.

Each row says: "this project requires skill X at difficulty_rating D."
difficulty_rating uses the same numeric scale as EmployeeSkill.rating,
so the Elo expected-success formula can compare them directly.

Difficulty mapping (IDEA.md §4.2, from config):
  low=900, medium=1200, high=1600, expert=2000
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.skill import Skill


class ProjectSkillRequirement(Base):
    __tablename__ = "project_skill_requirements"
    __table_args__ = (
        UniqueConstraint("project_id", "skill_id", name="uq_project_skill"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    skill_id: Mapped[int] = mapped_column(
        # RESTRICT: don't allow deleting a skill that's referenced by a project
        ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    # Same scale as EmployeeSkill.rating — enables direct Elo comparison
    difficulty_rating: Mapped[float] = mapped_column(Float, nullable=False)

    # ── Relationships ─────────────────────────────────────────────────────────
    project: Mapped[Project] = relationship(
        "Project", back_populates="skill_requirements"
    )
    skill: Mapped[Skill] = relationship(
        "Skill", back_populates="project_requirements"
    )

    def __repr__(self) -> str:
        return (
            f"<ProjectSkillRequirement project_id={self.project_id} "
            f"skill_id={self.skill_id} difficulty={self.difficulty_rating}>"
        )
