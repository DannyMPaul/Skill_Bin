"""initial_tables

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-06-18 06:10:00 UTC

Creates all tables defined in IDEA.md §3:
  employers, employees, skills, employee_skills,
  projects, project_skill_requirements,
  match_recommendations, task_outcomes, verification_tests

Design notes:
- Enum columns use native_enum=False (VARCHAR + CHECK constraint) so
  adding new enum values later only requires an ALTER TABLE, not a
  PostgreSQL ALTER TYPE.
- candidates_json / rating_changes_json use JSONB for efficient querying.
- employer_id on employees and projects enables multi-tenancy queries
  (Phase 5 security requirement).
- Tables are created in dependency order so FK constraints are satisfied.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from alembic import op

# revision identifiers
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── 1. employers ──────────────────────────────────────────────────────────
    op.create_table(
        "employers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_employers_email", "employers", ["email"], unique=True)

    # ── 2. skills (shared taxonomy — no employer FK) ──────────────────────────
    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_skills_name", "skills", ["name"], unique=True)

    # ── 3. employees ──────────────────────────────────────────────────────────
    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("employer_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("raw_resume_text", sa.Text(), nullable=True),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["employer_id"], ["employers.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_employees_employer_id", "employees", ["employer_id"], unique=False
    )

    # ── 4. projects ───────────────────────────────────────────────────────────
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("employer_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        # VARCHAR + CHECK instead of native PG ENUM — easier to extend
        sa.Column("status", sa.String(length=15), nullable=False),
        sa.Column("assigned_employee_id", sa.Integer(), nullable=True),
        sa.Column("deadline", sa.Date(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('unassigned','assigned','in_progress','completed')",
            name="ck_projects_status",
        ),
        sa.ForeignKeyConstraint(
            ["assigned_employee_id"], ["employees.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["employer_id"], ["employers.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_projects_employer_id", "projects", ["employer_id"], unique=False
    )
    op.create_index(
        "ix_projects_assigned_employee_id",
        "projects",
        ["assigned_employee_id"],
        unique=False,
    )

    # ── 5. employee_skills ────────────────────────────────────────────────────
    op.create_table(
        "employee_skills",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Float(), nullable=False),
        sa.Column("rating_deviation", sa.Float(), nullable=False),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column(
            "last_updated",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "source IN ('resume_seed','task_outcome','verification_test')",
            name="ck_employee_skills_source",
        ),
        sa.ForeignKeyConstraint(
            ["employee_id"], ["employees.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["skill_id"], ["skills.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint("employee_id", "skill_id", name="uq_employee_skill"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_employee_skills_employee_id",
        "employee_skills",
        ["employee_id"],
        unique=False,
    )
    op.create_index(
        "ix_employee_skills_skill_id", "employee_skills", ["skill_id"], unique=False
    )

    # ── 6. project_skill_requirements ─────────────────────────────────────────
    op.create_table(
        "project_skill_requirements",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("difficulty_rating", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id"], ["projects.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["skill_id"], ["skills.id"], ondelete="RESTRICT"
        ),
        sa.UniqueConstraint("project_id", "skill_id", name="uq_project_skill"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_project_skill_requirements_project_id",
        "project_skill_requirements",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        "ix_project_skill_requirements_skill_id",
        "project_skill_requirements",
        ["skill_id"],
        unique=False,
    )

    # ── 7. match_recommendations ──────────────────────────────────────────────
    op.create_table(
        "match_recommendations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column(
            "generated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        # JSONB: ranked candidate list with scores and per-skill breakdown
        sa.Column(
            "candidates_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("chosen_employee_id", sa.Integer(), nullable=True),
        sa.Column("employer_override", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["chosen_employee_id"], ["employees.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["project_id"], ["projects.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_match_recommendations_project_id",
        "match_recommendations",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        "ix_match_recommendations_chosen_employee_id",
        "match_recommendations",
        ["chosen_employee_id"],
        unique=False,
    )

    # ── 8. task_outcomes ──────────────────────────────────────────────────────
    op.create_table(
        "task_outcomes",
        sa.Column("id", sa.Integer(), nullable=False),
        # unique=True: one project → one outcome, enforced at DB level
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("outcome", sa.String(length=10), nullable=False),
        sa.Column("quality_note", sa.Text(), nullable=True),
        # JSONB: before/after per-skill ratings for the audit trail
        sa.Column(
            "rating_changes_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "outcome IN ('success','partial','fail')",
            name="ck_task_outcomes_outcome",
        ),
        sa.ForeignKeyConstraint(
            ["employee_id"], ["employees.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["project_id"], ["projects.id"], ondelete="CASCADE"
        ),
        sa.UniqueConstraint("project_id", name="uq_task_outcome_project"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_task_outcomes_employee_id", "task_outcomes", ["employee_id"], unique=False
    )

    # ── 9. verification_tests (Phase 8 stretch — schema exists from day 1) ───
    op.create_table(
        "verification_tests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("generated_prompt", sa.Text(), nullable=False),
        sa.Column("employer_recorded_score", sa.Float(), nullable=True),
        sa.Column("applied", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["employee_id"], ["employees.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["skill_id"], ["skills.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_verification_tests_employee_id",
        "verification_tests",
        ["employee_id"],
        unique=False,
    )
    op.create_index(
        "ix_verification_tests_skill_id",
        "verification_tests",
        ["skill_id"],
        unique=False,
    )


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_table("verification_tests")
    op.drop_table("task_outcomes")
    op.drop_table("match_recommendations")
    op.drop_table("project_skill_requirements")
    op.drop_table("employee_skills")
    op.drop_table("projects")
    op.drop_table("employees")
    op.drop_table("skills")
    op.drop_table("employers")
