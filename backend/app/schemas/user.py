"""User request / response schemas."""

from pydantic import EmailStr, Field, field_validator

from app.core.security import Role
from app.schemas.base import AppBaseModel, IDSchema, TimestampSchema


class UserCreate(AppBaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100, pattern=r"^[a-zA-Z0-9_-]+$")
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)
    role: Role = Role.VIEWER

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserUpdate(AppBaseModel):
    full_name: str | None = Field(None, max_length=255)
    role: Role | None = None
    is_active: bool | None = None


class UserResponse(IDSchema, TimestampSchema):
    email: str
    username: str
    full_name: str
    role: Role
    is_active: bool
    is_verified: bool


class UserSummary(IDSchema):
    """Lightweight user reference used in nested responses."""
    username: str
    full_name: str
    role: Role
