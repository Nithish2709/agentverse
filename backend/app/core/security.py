"""JWT token creation, validation, and RBAC permission definitions."""

from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

from jose import JWTError, jwt
from pydantic import BaseModel

from app.config import get_settings
from app.core.exceptions import AuthenticationError


# ── RBAC ─────────────────────────────────────────────────────────────────────

class Role(StrEnum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    ANALYST = "analyst"
    FIELD_OFFICER = "field_officer"
    VIEWER = "viewer"


class Permission(StrEnum):
    # User management
    USER_READ = "user:read"
    USER_WRITE = "user:write"
    USER_DELETE = "user:delete"
    # Reports
    REPORT_READ = "report:read"
    REPORT_WRITE = "report:write"
    # Agents (future)
    AGENT_TRIGGER = "agent:trigger"
    AGENT_READ = "agent:read"
    # System
    SYSTEM_ADMIN = "system:admin"


ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.SUPER_ADMIN: set(Permission),
    Role.ADMIN: {
        Permission.USER_READ, Permission.USER_WRITE,
        Permission.REPORT_READ, Permission.REPORT_WRITE,
        Permission.AGENT_READ, Permission.AGENT_TRIGGER,
    },
    Role.ANALYST: {
        Permission.USER_READ,
        Permission.REPORT_READ, Permission.REPORT_WRITE,
        Permission.AGENT_READ,
    },
    Role.FIELD_OFFICER: {
        Permission.REPORT_READ, Permission.REPORT_WRITE,
    },
    Role.VIEWER: {
        Permission.REPORT_READ,
        Permission.USER_READ,
    },
}


def get_permissions_for_role(role: Role) -> set[Permission]:
    return ROLE_PERMISSIONS.get(role, set())


# ── Token schemas ─────────────────────────────────────────────────────────────

class TokenPayload(BaseModel):
    sub: str                        # user id
    role: Role
    permissions: list[Permission]
    exp: datetime
    iat: datetime
    jti: str                        # JWT ID for revocation support


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int                 # seconds


# ── Token operations ──────────────────────────────────────────────────────────

def _build_payload(
    subject: str,
    role: Role,
    expire_delta: timedelta,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    import uuid
    now = datetime.now(UTC)
    permissions = [p.value for p in get_permissions_for_role(role)]
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role.value,
        "permissions": permissions,
        "iat": now,
        "exp": now + expire_delta,
        "jti": str(uuid.uuid4()),
    }
    if extra:
        payload.update(extra)
    return payload


def create_access_token(subject: str, role: Role) -> str:
    settings = get_settings()
    payload = _build_payload(
        subject, role, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(subject: str, role: Role) -> str:
    settings = get_settings()
    payload = _build_payload(
        subject, role, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        extra={"type": "refresh"},
    )
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_token_pair(subject: str, role: Role) -> TokenPair:
    settings = get_settings()
    return TokenPair(
        access_token=create_access_token(subject, role),
        refresh_token=create_refresh_token(subject, role),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


def decode_token(token: str) -> TokenPayload:
    settings = get_settings()
    try:
        raw = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return TokenPayload(
            sub=raw["sub"],
            role=Role(raw["role"]),
            permissions=[Permission(p) for p in raw.get("permissions", [])],
            exp=datetime.fromtimestamp(raw["exp"], tz=UTC),
            iat=datetime.fromtimestamp(raw["iat"], tz=UTC),
            jti=raw["jti"],
        )
    except (JWTError, KeyError, ValueError) as exc:
        raise AuthenticationError("Invalid or expired token") from exc
