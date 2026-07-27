"""Health check endpoint — liveness and readiness probes."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.config import get_settings
from app.database.redis import check_redis_connection
from app.database.session import check_db_connection

router = APIRouter(tags=["health"])


class ComponentStatus(BaseModel):
    status: str
    detail: str | None = None


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    components: dict[str, ComponentStatus]


@router.get("/health", response_model=HealthResponse, summary="Readiness probe")
async def health_check() -> HealthResponse:
    settings = get_settings()
    db_ok = await check_db_connection()
    redis_ok = await check_redis_connection()

    overall = "healthy" if db_ok and redis_ok else "degraded"

    return HealthResponse(
        status=overall,
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        components={
            "database": ComponentStatus(
                status="ok" if db_ok else "error",
                detail=None if db_ok else "PostgreSQL unreachable",
            ),
            "cache": ComponentStatus(
                status="ok" if redis_ok else "error",
                detail=None if redis_ok else "Redis unreachable",
            ),
        },
    )


@router.get("/ping", summary="Liveness probe")
async def ping() -> dict[str, str]:
    return {"ping": "pong"}
