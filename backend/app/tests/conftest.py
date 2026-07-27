"""Pytest configuration — shared fixtures for unit and integration tests."""

import asyncio
from collections.abc import AsyncGenerator
from typing import Any
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.database.session import Base, get_db
from app.main import create_app


# ── Event loop ────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def event_loop_policy():
    return asyncio.DefaultEventLoopPolicy()


# ── In-memory SQLite engine for unit tests ────────────────────────────────────

@pytest_asyncio.fixture(scope="function")
async def test_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    factory = async_sessionmaker(test_engine, expire_on_commit=False)
    async with factory() as session:
        yield session


# ── FastAPI test client ───────────────────────────────────────────────────────

@pytest_asyncio.fixture(scope="function")
async def app(db_session: AsyncSession) -> FastAPI:
    application = create_app()

    async def _override_get_db():
        yield db_session

    application.dependency_overrides[get_db] = _override_get_db
    return application


@pytest_asyncio.fixture(scope="function")
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


# ── Mock Redis ────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_redis() -> AsyncMock:
    redis = AsyncMock()
    redis.ping.return_value = True
    redis.get.return_value = None
    redis.set.return_value = True
    redis.delete.return_value = 1
    redis.exists.return_value = 0
    redis.incr.return_value = 1
    return redis
