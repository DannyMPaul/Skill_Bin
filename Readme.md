# SkillBin — AI-Powered Task Allocation & Skill Rating Engine

> Working name — rename freely once you've got something you like better.

## What this is

SkillBin is a demo system where an employer manages a pool of employees (represented by their resumes) and a stream of incoming tasks. An AI agent — "the Bin" — reads each employee's resume into structured, per-skill ratings, reads each task's required skills and difficulty, and recommends who should do the work: not just who's free, but who's actually best suited, without overloading anyone. Completing a task updates the employee's skill rating using a chess-style (Elo/Glicko-inspired) system, so the leaderboard reflects difficulty handled, not number of tasks completed.

This project was built as a portfolio piece to demonstrate applied LLM integration, system design, and algorithmic thinking beyond CRUD — see [`IDEA.md`](./IDEA.md) for the full design rationale.

## How it works, briefly

1. Employer pastes an employee's resume → Claude extracts skills/experience/certifications as structured facts → a deterministic local algorithm converts those facts into an initial skill rating (with an explicit confidence/uncertainty measure).
2. Employer creates a task → required skills and difficulty are set (manually, or AI-assisted from the description).
3. The Bin filters out overloaded employees, scores everyone else's likely success against the task's difficulty per required skill, and recommends the best fit with a transparent explanation.
4. Employer assigns, the work happens, employer records the outcome, and the employee's rating updates — a hard task done well moves the needle far more than an easy one.
5. Leaderboards and growth views reflect difficulty-weighted skill, not raw task count.

## Tech stack

- **Backend:** Python, FastAPI, SQLAlchemy + Alembic, PostgreSQL
- **Frontend:** React (Vite)
- **AI:** Claude API (Anthropic) for structured resume/task parsing
- **Auth:** JWT-based employer login (single real user role in v1)

## Project structure

```
backend/
  app/
    models/        # SQLAlchemy models
    routers/        # FastAPI route handlers
    services/        # matching algorithm, rating math, Claude integration
    core/             # config, auth, db session
  tests/
frontend/
  src/
    pages/
    components/
    api/
IDEA.md       # full concept & design rationale
PHASES.md     # build plan, executed one phase at a time
CLAUDE.md     # operating rules for the AI implementing this
```

## Getting started

1. Copy `.env.example` to `.env` and fill in `DATABASE_URL`, `ANTHROPIC_API_KEY`, `JWT_SECRET`, `CORS_ORIGIN`.
2. Backend: `cd backend && pip install -r requirements.txt && alembic upgrade head && uvicorn app.main:app --reload`
3. Frontend: `cd frontend && npm install && npm run dev`
4. (Optional) `python scripts/seed_demo_data.py` to populate sample employees and tasks.

## Core design decisions worth highlighting

- **The rating system is Elo/Glicko-inspired**, not a hand-tuned points formula — difficulty-weighting falls out of the math by construction instead of needing fragile manual weighting rules.
- **The LLM only ever extracts facts, never outputs numeric ratings directly** — a deterministic, unit-tested local function does the actual scoring, so every rating is fully auditable and reproducible.
- **Workload is a hard filter, not a soft signal** — an overloaded employee is excluded from recommendations entirely rather than just scored lower.

## Status

v1 (single-employer demo, placeholder employee profiles). See [`PHASES.md`](./PHASES.md) for what's built and what's left.

## Future / production considerations (deliberately out of scope for v1)

- Real employee accounts with self-service resume upload and skill-test taking.
- Multi-tenant support for multiple employers.
- Automated bias/disparate-impact auditing of the matching algorithm.
- Difficulty recalibration based on real outcome variance across the employee pool, rather than a static employer-set difficulty.
- Formal legal-compliance tooling (audit retention, regulatory reporting) for jurisdictions that regulate automated employment decision tools.

## License

MIT (or your preference).
