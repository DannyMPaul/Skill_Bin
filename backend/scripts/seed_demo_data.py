"""
scripts/seed_demo_data.py — Populate the database with realistic demo data.

IDEMPOTENT: safe to run multiple times. Skills are upserted by name;
the demo employer is skipped if the email already exists; employees
are skipped if the name already exists under that employer.

Usage (run from backend/):
    uv run python scripts/seed_demo_data.py

What it creates:
  - 15 skills (shared taxonomy)
  - 1 demo employer  (demo@skillbin.local / demo1234)
  - 3 demo employees with resume-seeded skill ratings
  - 2 demo projects (unassigned, ready to test the Bin in Phase 5)

The demo employees model the IDEA.md example walkthrough (§7):
  Priya S.   — Python specialist, 4 yrs + AWS cert + high-complexity project
  Marcus T.  — JS/React frontend developer, 2 yrs + medium project
  Aisha K.   — Project manager, 4 yrs + PMP cert + 2 high-complexity projects
"""

import os
import sys
from datetime import datetime, timezone

# ── Make `app` importable when running from backend/ ─────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from passlib.context import CryptContext  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.db import SessionLocal  # noqa: E402
from app.models import (  # noqa: E402
    Employer,
    Employee,
    Skill,
    EmployeeSkill,
    Project,
    ProjectSkillRequirement,
    SkillSource,
    ProjectStatus,
)
from app.core.config import settings  # noqa: E402

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── Demo data definitions ──────────────────────────────────────────────────────

DEMO_SKILLS = [
    "Python", "JavaScript", "TypeScript", "React", "FastAPI",
    "PostgreSQL", "AWS", "Docker", "System Design", "Project Management",
    "Machine Learning", "Git", "REST APIs", "Node.js", "Redis",
]

DEMO_EMPLOYER = {
    "email": "demo@skillbin.local",
    "password": "demo1234",   # hashed below — never stored in plaintext
}

# Each employee definition maps skill names to (rating, rating_deviation).
# Ratings computed per IDEA.md §5.2 seeding formula for illustration:
#   base=1000, +50/yr (cap 400), +75/cert, +30/65/100 per low/med/high project
DEMO_EMPLOYEES = [
    {
        "name": "Priya Sharma",
        "raw_resume_text": (
            "Senior Python Engineer with 4 years of experience. "
            "AWS Certified Solutions Architect. "
            "Led a high-complexity backend migration from monolith to microservices. "
            "Strong PostgreSQL and REST API skills."
        ),
        "capacity": 3,
        "skills": {
            # 1000 + 200(4yrs) + 75(AWS cert) + 100(high project) = 1375, RD=350
            "Python":     (1375.0, 350.0),
            # 1000 + 75(cert) + 100(high) = 1175, RD=350
            "AWS":        (1175.0, 350.0),
            # 1000 + 200(4yrs) + 100(high) = 1300, RD=350
            "PostgreSQL": (1300.0, 350.0),
            "REST APIs":  (1100.0, 350.0),
        },
    },
    {
        "name": "Marcus Thompson",
        "raw_resume_text": (
            "Frontend Developer with 2 years of experience in JavaScript and React. "
            "Delivered a medium-complexity e-commerce dashboard project. "
            "Node.js backend experience. TypeScript advocate."
        ),
        "capacity": 3,
        "skills": {
            # 1000 + 100(2yrs) + 65(medium project) = 1165, RD=350
            "JavaScript": (1165.0, 350.0),
            "TypeScript": (1080.0, 350.0),
            # 1000 + 100(2yrs) + 65(medium) = 1165, RD=350
            "React":      (1165.0, 350.0),
            "Node.js":    (1050.0, 350.0),
        },
    },
    {
        "name": "Aisha Khan",
        "raw_resume_text": (
            "Senior Project Manager with 4 years of experience. "
            "PMP certified. Managed two high-complexity digital transformation projects. "
            "Strong system design and stakeholder management skills."
        ),
        "capacity": 3,
        "skills": {
            # 1000 + 200(4yrs) + 75(PMP) + 100(high) + 100(high) = 1475, RD=350
            "Project Management": (1475.0, 350.0),
            # 1000 + 200(4yrs) + 100(high) = 1300, RD=350
            "System Design":      (1300.0, 350.0),
            "Git":                (1050.0, 350.0),
        },
    },
]

DEMO_PROJECTS = [
    {
        "title": "Refactor payment service",
        "description": (
            "Decompose the legacy payment monolith into two microservices "
            "(charge and reconciliation). Migrate to PostgreSQL, add retry logic, "
            "and improve test coverage to 80%+."
        ),
        "skill_requirements": {
            # 'high' difficulty = 1600 per config
            "Python":     settings.difficulty_high,
            "PostgreSQL": settings.difficulty_medium,
        },
    },
    {
        "title": "Build team dashboard UI",
        "description": (
            "Create a React dashboard showing real-time project status, "
            "team workload heatmap, and skill leaderboard. TypeScript required."
        ),
        "skill_requirements": {
            "React":      settings.difficulty_medium,
            "TypeScript": settings.difficulty_low,
        },
    },
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_or_create_skill(db: Session, name: str) -> Skill:
    """Return existing Skill by name, or create a new one (normalised)."""
    normalised = name.strip().title()
    skill = db.query(Skill).filter(Skill.name == normalised).first()
    if not skill:
        skill = Skill(name=normalised)
        db.add(skill)
        db.flush()
    return skill


def seed_skills(db: Session) -> dict[str, Skill]:
    """Upsert the full skill taxonomy. Returns name→Skill mapping."""
    print("\n[skills]")
    skill_map: dict[str, Skill] = {}
    for name in DEMO_SKILLS:
        skill = get_or_create_skill(db, name)
        skill_map[skill.name] = skill
        print(f"  ✓ {skill.name}")
    return skill_map


def seed_employer(db: Session) -> Employer:
    """Create the demo employer if it doesn't exist."""
    print("\n[employer]")
    employer = db.query(Employer).filter(
        Employer.email == DEMO_EMPLOYER["email"]
    ).first()

    if employer:
        print(f"  ↩ {DEMO_EMPLOYER['email']} already exists (id={employer.id})")
        return employer

    employer = Employer(
        email=DEMO_EMPLOYER["email"],
        password_hash=pwd_context.hash(DEMO_EMPLOYER["password"]),
    )
    db.add(employer)
    db.flush()
    print(f"  ✓ Created {DEMO_EMPLOYER['email']} (id={employer.id})")
    print(f"    Password: {DEMO_EMPLOYER['password']}  ← change before any real use")
    return employer


def seed_employees(
    db: Session, employer: Employer, skill_map: dict[str, Skill]
) -> dict[str, Employee]:
    """Create demo employees with seeded skill ratings."""
    print("\n[employees]")
    employee_map: dict[str, Employee] = {}

    for emp_data in DEMO_EMPLOYEES:
        existing = (
            db.query(Employee)
            .filter(
                Employee.employer_id == employer.id,
                Employee.name == emp_data["name"],
            )
            .first()
        )
        if existing:
            print(f"  ↩ {emp_data['name']} already exists (id={existing.id})")
            employee_map[emp_data["name"]] = existing
            continue

        employee = Employee(
            employer_id=employer.id,
            name=emp_data["name"],
            raw_resume_text=emp_data["raw_resume_text"],
            capacity=emp_data["capacity"],
        )
        db.add(employee)
        db.flush()

        # Seed skill ratings (deterministic — no LLM involved here)
        for skill_name, (rating, rd) in emp_data["skills"].items():
            skill = skill_map.get(skill_name)
            if not skill:
                print(f"  ⚠  Skill '{skill_name}' not in taxonomy — skipping")
                continue
            # Skip if already seeded (idempotency for partial re-runs)
            existing_es = (
                db.query(EmployeeSkill)
                .filter(
                    EmployeeSkill.employee_id == employee.id,
                    EmployeeSkill.skill_id == skill.id,
                )
                .first()
            )
            if not existing_es:
                db.add(
                    EmployeeSkill(
                        employee_id=employee.id,
                        skill_id=skill.id,
                        rating=rating,
                        rating_deviation=rd,
                        source=SkillSource.RESUME_SEED,
                    )
                )

        db.flush()
        skills_summary = ", ".join(
            f"{sn}={r:.0f}" for sn, (r, _) in emp_data["skills"].items()
        )
        print(f"  ✓ {emp_data['name']} (id={employee.id}) — {skills_summary}")
        employee_map[emp_data["name"]] = employee

    return employee_map


def seed_projects(
    db: Session, employer: Employer, skill_map: dict[str, Skill]
) -> None:
    """Create demo projects with skill requirements."""
    print("\n[projects]")
    for proj_data in DEMO_PROJECTS:
        existing = (
            db.query(Project)
            .filter(
                Project.employer_id == employer.id,
                Project.title == proj_data["title"],
            )
            .first()
        )
        if existing:
            print(f"  ↩ '{proj_data['title']}' already exists (id={existing.id})")
            continue

        project = Project(
            employer_id=employer.id,
            title=proj_data["title"],
            description=proj_data["description"],
            status=ProjectStatus.UNASSIGNED,
        )
        db.add(project)
        db.flush()

        for skill_name, difficulty in proj_data["skill_requirements"].items():
            skill = skill_map.get(skill_name)
            if not skill:
                print(f"  ⚠  Skill '{skill_name}' not found — skipping requirement")
                continue
            db.add(
                ProjectSkillRequirement(
                    project_id=project.id,
                    skill_id=skill.id,
                    difficulty_rating=float(difficulty),
                )
            )

        db.flush()
        reqs = ", ".join(
            f"{sn}@{d}" for sn, d in proj_data["skill_requirements"].items()
        )
        print(f"  ✓ '{proj_data['title']}' (id={project.id}) — requires: {reqs}")


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 60)
    print("SkillBin seed script")
    print("=" * 60)

    db: Session = SessionLocal()
    try:
        skill_map = seed_skills(db)
        employer = seed_employer(db)
        seed_employees(db, employer, skill_map)
        seed_projects(db, employer, skill_map)

        db.commit()
        print("\n✅ Seed complete. All data committed.")
        print(
            f"\nDemo login: {DEMO_EMPLOYER['email']} / {DEMO_EMPLOYER['password']}"
        )
    except Exception:
        db.rollback()
        print("\n❌ Seed failed — rolled back. See traceback above.")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
