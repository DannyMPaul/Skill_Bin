"""
app/core/config.py — Single source of truth for all configuration.

All settings are read from environment variables (via .env).
No other module should call os.environ or os.getenv directly —
import `settings` from here instead.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Extra fields in .env are silently ignored
        extra="ignore",
    )

    # ── Core infrastructure ────────────────────────────────────────────────
    database_url: str
    anthropic_api_key: str
    jwt_secret: str
    cors_origin: str

    # ── JWT ────────────────────────────────────────────────────────────────
    jwt_algorithm: str = "HS256"
    # Token lifetime in minutes (default: 8 hours — long enough for a work day)
    jwt_access_token_expire_minutes: int = 480

    # ── Claude API ────────────────────────────────────────────────────────
    # Model to use for structured extraction (IDEA.md §4.1, §4.2)
    claude_model: str = "claude-opus-4-5"
    # Hard cap on resume text sent to the API (chars) — cost + abuse control
    claude_max_resume_length: int = 15_000
    # Hard cap on task description sent to the API
    claude_max_description_length: int = 5_000
    # Seconds before we give up on a Claude call and return a graceful error
    claude_api_timeout: int = 30

    # ── Rating algorithm constants (IDEA.md §5.2) ─────────────────────────
    # All constants live here so they're easy to audit, tune, and test.
    rating_base: int = 1_000
    rating_points_per_year: int = 50          # per year of experience
    rating_max_experience_bonus: int = 400    # cap on experience points
    rating_points_per_certification: int = 75
    rating_points_project_low: int = 30
    rating_points_project_medium: int = 65
    rating_points_project_high: int = 100
    rating_initial_deviation: int = 350       # high uncertainty for resume seeds

    # ── Rating update constants (IDEA.md §5.3) ────────────────────────────
    rating_base_k_factor: int = 40
    rating_deviation_min: int = 50            # RD floor — K never collapses to ~0
    rating_deviation_shrink_factor: float = 0.75  # RD * 0.75 after each outcome

    # ── Task difficulty mapping (IDEA.md §4.2) ────────────────────────────
    difficulty_low: int = 900
    difficulty_medium: int = 1_200
    difficulty_high: int = 1_600
    difficulty_expert: int = 2_000

    # ── Employee capacity default (IDEA.md §3) ────────────────────────────
    employee_default_capacity: int = 3


# Module-level singleton — import this everywhere
settings = Settings()
