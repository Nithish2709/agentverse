"""Rate limiting middleware using Redis sliding window counter."""

from collections.abc import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings
from app.database.redis import get_redis_client


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health probes
        if request.url.path in ("/health", "/ping"):
            return await call_next(request)

        settings = get_settings()
        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{client_ip}"

        try:
            redis = get_redis_client()
            count = await redis.incr(key)
            if count == 1:
                await redis.expire(key, settings.RATE_LIMIT_WINDOW_SECONDS)
            await redis.aclose()

            if count > settings.RATE_LIMIT_REQUESTS:
                return JSONResponse(
                    status_code=429,
                    content={"error": "RATE_LIMIT_EXCEEDED", "message": "Too many requests"},
                    headers={"Retry-After": str(settings.RATE_LIMIT_WINDOW_SECONDS)},
                )
        except Exception:
            # Fail open — don't block requests if Redis is unavailable
            pass

        return await call_next(request)
