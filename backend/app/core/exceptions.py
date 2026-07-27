"""Domain-level exception hierarchy for PDS Sentinel AI."""

from http import HTTPStatus


class AppError(Exception):
    """Base application exception."""

    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR
    error_code: str = "INTERNAL_ERROR"

    def __init__(self, message: str = "An unexpected error occurred") -> None:
        self.message = message
        super().__init__(message)


class NotFoundError(AppError):
    status_code = HTTPStatus.NOT_FOUND
    error_code = "NOT_FOUND"

    def __init__(self, resource: str, identifier: str | int) -> None:
        super().__init__(f"{resource} '{identifier}' not found")


class ConflictError(AppError):
    status_code = HTTPStatus.CONFLICT
    error_code = "CONFLICT"


class ValidationError(AppError):
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    error_code = "VALIDATION_ERROR"


class AuthenticationError(AppError):
    status_code = HTTPStatus.UNAUTHORIZED
    error_code = "AUTHENTICATION_ERROR"

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message)


class AuthorizationError(AppError):
    status_code = HTTPStatus.FORBIDDEN
    error_code = "AUTHORIZATION_ERROR"

    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__(message)


class RateLimitError(AppError):
    status_code = HTTPStatus.TOO_MANY_REQUESTS
    error_code = "RATE_LIMIT_EXCEEDED"

    def __init__(self) -> None:
        super().__init__("Rate limit exceeded. Please try again later.")


class ServiceUnavailableError(AppError):
    status_code = HTTPStatus.SERVICE_UNAVAILABLE
    error_code = "SERVICE_UNAVAILABLE"
