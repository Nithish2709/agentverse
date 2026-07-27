"""Core package — re-exports for convenience."""

from app.core.exceptions import (
    AppError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    NotFoundError,
    RateLimitError,
    ServiceUnavailableError,
    ValidationError,
)
from app.core.hashing import hash_password, verify_password
from app.core.logging import configure_logging, get_logger
from app.core.security import (
    Permission,
    Role,
    TokenPair,
    TokenPayload,
    create_token_pair,
    decode_token,
    get_permissions_for_role,
)

__all__ = [
    "AppError",
    "AuthenticationError",
    "AuthorizationError",
    "ConflictError",
    "NotFoundError",
    "RateLimitError",
    "ServiceUnavailableError",
    "ValidationError",
    "hash_password",
    "verify_password",
    "configure_logging",
    "get_logger",
    "Permission",
    "Role",
    "TokenPair",
    "TokenPayload",
    "create_token_pair",
    "decode_token",
    "get_permissions_for_role",
]
