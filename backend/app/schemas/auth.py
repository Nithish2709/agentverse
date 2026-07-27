"""Auth request / response schemas."""

from pydantic import EmailStr

from app.core.security import TokenPair
from app.schemas.base import AppBaseModel


class LoginRequest(AppBaseModel):
    email: EmailStr
    password: str


class TokenResponse(AppBaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(AppBaseModel):
    refresh_token: str
