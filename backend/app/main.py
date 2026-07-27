"""FastAPI application factory."""

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.middleware.exception_handler import ExceptionHandlerMiddleware
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    configure_logging()
    settings = get_settings()
    logger.info("startup", app=settings.APP_NAME, version=settings.APP_VERSION, env=settings.APP_ENV)
    yield
    logger.info("shutdown", app=settings.APP_NAME)


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Agentic AI platform for monitoring the Public Distribution System",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        lifespan=lifespan,
    )

    # ── Middleware (order matters — outermost first) ───────────────────────────
    app.add_middleware(ExceptionHandlerMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=settings.ALLOWED_METHODS,
        allow_headers=settings.ALLOWED_HEADERS,
    )

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(api_v1_router, prefix=settings.API_V1_PREFIX)

    return app
