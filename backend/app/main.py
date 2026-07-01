"""
app/main.py — FastAPI application entry point.

Changes from Phase 0:
  - Auth router registered at /api/v1
  - Global exception handler — unhandled 500s log the full traceback server-side
    but return only a generic JSON message to the client (CLAUDE.md requirement).
"""
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.routers import auth as auth_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="SkillBin API",
    description=(
        "AI-powered task allocation and skill rating engine. "
        "See /docs for the interactive API reference."
    ),
    version="0.2.0",
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

# ── Global exception handler ──────────────────────────────────────────────────
# Catches any unhandled exception, logs it fully server-side, returns a generic
# 500 to the client — no stack traces, no internal details leaked (CLAUDE.md).
@app.exception_handler(Exception)
async def _global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "Unhandled exception on %s %s: %s",
        request.method,
        request.url.path,
        exc,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth_router.router, prefix="/api/v1")

# Future phases will add:
#   app.include_router(employees_router.router, prefix="/api/v1")   # Phase 3
#   app.include_router(projects_router.router,  prefix="/api/v1")   # Phase 4
#   app.include_router(matching_router.router,  prefix="/api/v1")   # Phase 5
#   app.include_router(outcomes_router.router,  prefix="/api/v1")   # Phase 6
#   app.include_router(dashboard_router.router, prefix="/api/v1")   # Phase 7


# ── Health check ─────────────────────────────────────────────────────────────
@app.get("/health", tags=["system"])
def health_check() -> dict:
    """Liveness probe — no auth required."""
    return {"status": "ok", "version": "0.2.0"}
