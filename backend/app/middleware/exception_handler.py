"""Global exception handler middleware — maps domain errors to JSON responses."""

import traceback
from collections.abc import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.exceptions import AppError
from app.core.logging import get_logger

logger = get_logger(__name__)


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except AppError as exc:
            logger.warning(
                "domain_error",
                error_code=exc.error_code,
                message=exc.message,
                path=request.url.path,
            )
            return JSONResponse(
                status_code=exc.status_code,
                content={"error": exc.error_code, "message": exc.message},
            )
        except Exception as exc:
            logger.error(
                "unhandled_exception",
                exc_info=True,
                path=request.url.path,
                traceback=traceback.format_exc(),
            )
            return JSONResponse(
                status_code=500,
                content={"error": "INTERNAL_ERROR", "message": "An unexpected error occurred"},
            )
