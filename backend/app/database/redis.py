"""Redis connection pool and helper utilities."""

from collections.abc import AsyncGenerator
from typing import Any

import redis.asyncio as aioredis

from app.config import get_settings


def _create_redis_pool() -> aioredis.ConnectionPool:
    settings = get_settings()
    return aioredis.ConnectionPool.from_url(
        settings.redis_url_str,
        max_connections=settings.REDIS_MAX_CONNECTIONS,
        decode_responses=True,
    )


_pool: aioredis.ConnectionPool | None = None


def get_pool() -> aioredis.ConnectionPool:
    global _pool  # noqa: PLW0603
    if _pool is None:
        _pool = _create_redis_pool()
    return _pool


def get_redis_client() -> aioredis.Redis:
    return aioredis.Redis(connection_pool=get_pool())


async def get_redis() -> AsyncGenerator[aioredis.Redis, None]:
    """FastAPI dependency — yields a Redis client."""
    client = get_redis_client()
    try:
        yield client
    finally:
        await client.aclose()


async def check_redis_connection() -> bool:
    """Return True if Redis is reachable."""
    try:
        client = get_redis_client()
        await client.ping()
        await client.aclose()
        return True
    except Exception:
        return False


class CacheService:
    """Thin wrapper around Redis for typed cache operations."""

    def __init__(self, client: aioredis.Redis) -> None:
        self._client = client

    async def get(self, key: str) -> str | None:
        return await self._client.get(key)

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        settings = get_settings()
        await self._client.set(key, value, ex=ttl or settings.CACHE_TTL_SECONDS)

    async def delete(self, key: str) -> None:
        await self._client.delete(key)

    async def exists(self, key: str) -> bool:
        return bool(await self._client.exists(key))

    async def increment(self, key: str, ttl: int | None = None) -> int:
        count = await self._client.incr(key)
        if count == 1 and ttl:
            await self._client.expire(key, ttl)
        return count
