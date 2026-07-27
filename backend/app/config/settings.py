"""Application settings using Pydantic Settings for environment variable management."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    APP_NAME: str = "PDS Sentinel AI"
    APP_VERSION: str = "0.1.0"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # ── Security ─────────────────────────────────────────────────────────────
    SECRET_KEY: str = Field(..., min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── Database ─────────────────────────────────────────────────────────────
    DATABASE_URL: PostgresDsn
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_ECHO: bool = False

    # ── Redis ─────────────────────────────────────────────────────────────────
    REDIS_URL: RedisDsn
    REDIS_MAX_CONNECTIONS: int = 20
    CACHE_TTL_SECONDS: int = 300

    # ── CORS ─────────────────────────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    ALLOWED_METHODS: list[str] = ["*"]
    ALLOWED_HEADERS: list[str] = ["*"]

    # ── Logging ───────────────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: Literal["json", "text"] = "json"

    # ── Rate Limiting ─────────────────────────────────────────────────────────
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    @field_validator("DATABASE_ECHO", mode="before")
    @classmethod
    def set_db_echo(cls, v: bool, info) -> bool:  # noqa: ANN001
        # Only echo SQL in development
        return v

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def database_url_str(self) -> str:
        return str(self.DATABASE_URL)

    @property
    def redis_url_str(self) -> str:
        return str(self.REDIS_URL)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()  # type: ignore[call-arg]
