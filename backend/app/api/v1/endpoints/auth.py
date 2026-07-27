"""Authentication endpoints — login and token refresh."""

from fastapi import APIRouter

from app.api.dependencies import UserServiceDep
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from app.core.security import decode_token, create_token_pair, Role

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse, summary="Obtain access token")
async def login(body: LoginRequest, svc: UserServiceDep) -> TokenResponse:
    pair = await svc.authenticate(body.email, body.password)
    return TokenResponse(
        access_token=pair.access_token,
        refresh_token=pair.refresh_token,
        expires_in=pair.expires_in,
    )


@router.post("/refresh", response_model=TokenResponse, summary="Refresh access token")
async def refresh_token(body: RefreshRequest) -> TokenResponse:
    payload = decode_token(body.refresh_token)
    pair = create_token_pair(payload.sub, Role(payload.role))
    return TokenResponse(
        access_token=pair.access_token,
        refresh_token=pair.refresh_token,
        expires_in=pair.expires_in,
    )
