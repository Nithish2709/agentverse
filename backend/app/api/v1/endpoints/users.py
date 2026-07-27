"""User management endpoints."""

from uuid import UUID

from fastapi import APIRouter

from app.api.dependencies import CurrentToken, UserServiceDep, require_permission
from app.core.security import Permission
from app.schemas.user import UserCreate, UserResponse, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=201,
    dependencies=[require_permission(Permission.USER_WRITE)],
    summary="Create a new user",
)
async def create_user(body: UserCreate, svc: UserServiceDep) -> UserResponse:
    user = await svc.create_user(body)
    return UserResponse.model_validate(user)


@router.get(
    "",
    response_model=list[UserResponse],
    dependencies=[require_permission(Permission.USER_READ)],
    summary="List users",
)
async def list_users(
    svc: UserServiceDep,
    limit: int = 100,
    offset: int = 0,
) -> list[UserResponse]:
    users = await svc.list_users(limit=limit, offset=offset)
    return [UserResponse.model_validate(u) for u in users]


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
)
async def get_me(token: CurrentToken, svc: UserServiceDep) -> UserResponse:
    user = await svc.get_user(UUID(token.sub))
    return UserResponse.model_validate(user)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[require_permission(Permission.USER_READ)],
    summary="Get user by ID",
)
async def get_user(user_id: UUID, svc: UserServiceDep) -> UserResponse:
    user = await svc.get_user(user_id)
    return UserResponse.model_validate(user)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    dependencies=[require_permission(Permission.USER_WRITE)],
    summary="Update user",
)
async def update_user(user_id: UUID, body: UserUpdate, svc: UserServiceDep) -> UserResponse:
    user = await svc.update_user(user_id, body)
    return UserResponse.model_validate(user)
