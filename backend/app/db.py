"""
app/db.py — Database engine, session factory, and FastAPI dependency.

All database access in route handlers goes through the `get_db` dependency.
No module should create its own engine or session — import from here.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings

engine = create_engine(
    settings.database_url,
    # Re-verify connections before using them from the pool —
    # prevents stale connection errors after DB restart.
    pool_pre_ping=True,
    # Keep pool size reasonable for a single-employer app.
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a DB session and guarantees cleanup.

    Usage in route handlers:
        db: Session = Depends(get_db)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
