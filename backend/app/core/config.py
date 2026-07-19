"""
Application configuration.

Why this file exists:
Every setting the app depends on (API keys, environment name, CORS origins, etc.)
should be defined in ONE place, loaded from environment variables, and typed —
not scattered as os.environ.get() calls across routes/services. That scattering
is one of the most common causes of "works on my machine" bugs.

We use pydantic-settings so that:
  1. Every setting is typed and validated at startup (fail fast, not at 2am in prod).
  2. Settings can be overridden via a .env file locally or real env vars in deployment,
     with zero code changes.
  3. Every other file imports `settings` from here instead of touching os.environ directly.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # General
    APP_NAME: str = "ArchGen AI"
    ENVIRONMENT: str = "development"  # development | production
    DEBUG: bool = True

    # CORS - which frontend origins are allowed to call this API.
    # Kept as a list now so adding a deployed frontend URL later is a one-line change.
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # AI provider - placeholder for now, wired up in Phase 1.
    GEMINI_API_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Instantiated once, imported everywhere. This is intentional - it's a
# singleton so we don't re-parse env vars on every request.
settings = Settings()
