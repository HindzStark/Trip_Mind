# ============================================================
# config.py — Loads settings from the .env file
# ============================================================
# FLOW: .env file  →  this file reads it  →  other files use `settings.DATABASE_URL`
#
# WHY? We never hardcode passwords or URLs in code.
#       We put them in .env, and this file reads them automatically.
#
# HOW? pydantic-settings reads .env and maps each variable
#       to a class attribute by matching the NAME.
#
#   .env has:          DATABASE_URL="postgresql+psycopg://..."
#   This class has:    DATABASE_URL: str
#   They match by name → pydantic fills in the value.
# ============================================================

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Each attribute here = one environment variable from .env
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",       # ← tells pydantic which file to read
        extra="ignore"         # ← ignore .env variables we didn't list above
    )


# Create one global instance — import this everywhere
settings = Settings()