"""FastAPI dependency injection — auth guards and service factories."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthorizationError
from app.core.security import Permission, TokenPayload, decode_token
from app.database.session import get_db
from app.services.user import UserService

_bearer = HTTPBearer(auto_error=True)


async def get_current_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
) -> TokenPayload:
    """Validate Bearer token and return its payload."""
    return decode_token(credentials.credentials)


async def get_user_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> UserService:
    return UserService(session)


# ── Typed dependency aliases ──────────────────────────────────────────────────

CurrentToken = Annotated[TokenPayload, Depends(get_current_token)]
DBSession = Annotated[AsyncSession, Depends(get_db)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]


# ── Permission guard factory ──────────────────────────────────────────────────

def require_permission(permission: Permission):
    """Return a FastAPI dependency that enforces a specific permission."""

    async def _guard(token: CurrentToken) -> TokenPayload:
        if permission not in token.permissions:
            raise AuthorizationError(
                f"Permission '{permission}' is required for this action"
            )
        return token

    return Depends(_guard)
