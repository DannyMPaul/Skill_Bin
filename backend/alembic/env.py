"""
alembic/env.py — Alembic migration environment.

Key design decisions:
- DATABASE_URL is always read from the app's Settings object (env var).
  It is NEVER read from alembic.ini's sqlalchemy.url placeholder.
- target_metadata points to Base.metadata so `alembic revision --autogenerate`
  can diff the current models against the DB schema.
- Both offline (SQL script) and online (live DB) migration modes are supported.
"""
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# ── Make the backend/app package importable ───────────────────────────────────
# alembic/ lives inside backend/, so we add backend/ to sys.path.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings  # noqa: E402
from app.models.base import Base       # noqa: E402
import app.models  # noqa: E402, F401 — ensures all models are registered on Base.metadata

# ── Alembic config object ─────────────────────────────────────────────────────
config = context.config

# Override the placeholder sqlalchemy.url with the real URL from settings.
# This is the one place where DATABASE_URL crosses from env → Alembic.
config.set_main_option("sqlalchemy.url", settings.database_url)

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata object that autogenerate will compare against.
target_metadata = Base.metadata


# ── Migration runners ─────────────────────────────────────────────────────────

def run_migrations_offline() -> None:
    """
    Run migrations without a live DB connection — outputs SQL to stdout.
    Useful for reviewing what will run before applying it.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations against a live DB connection — the normal path.
    Uses NullPool so Alembic doesn't hold connections open after finishing.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
