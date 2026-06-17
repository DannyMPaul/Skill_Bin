"""
app/main.py — FastAPI application entry point.

Responsibilities:
- Create the FastAPI app with metadata
- Register CORS middleware (origin from config — never hardcoded)
- Mount routers (added per phase)
- Expose the /health endpoint (no auth required)

Keep this file thin. Business logic lives in app/services/.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(
    title="SkillBin API",
    description=(
        "AI-powered task allocation and skill rating engine. "
        "See /docs for the interactive API reference."
    ),
    version="0.1.0",
    # Disable default docs in production if desired — fine to keep for now
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Origin is read from config — never hardcoded here.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
# Routers are added here as phases build them. Phase 0: none yet.
# Example (Phase 2):
#   from app.routers import auth
#   app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])


# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["system"])
def health_check() -> dict:
    """
    Liveness probe — no auth required.
    Returns 200 OK when the server is up.
    """
    return {"status": "ok", "version": "0.1.0"}
