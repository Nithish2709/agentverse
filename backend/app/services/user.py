"""User service — business logic layer between API and repository."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, ConflictError, NotFoundError
from app.core.hashing import hash_password, verify_password
from app.core.security import Role, TokenPair, create_token_pair
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = UserRepository(session)

    async def create_user(self, data: UserCreate) -> User:
        if await self._repo.get_by_email(data.email):
            raise ConflictError(f"Email '{data.email}' is already registered")
        if await self._repo.get_by_username(data.username):
            raise ConflictError(f"Username '{data.username}' is already taken")

        return await self._repo.create(
            email=data.email,
            username=data.username,
            hashed_password=hash_password(data.password),
            full_name=data.full_name,
            role=data.role.value,
        )

    async def authenticate(self, email: str, password: str) -> TokenPair:
        user = await self._repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")
        if not user.is_active:
            raise AuthenticationError("Account is disabled")
        return create_token_pair(str(user.id), Role(user.role))

    async def get_user(self, user_id: UUID) -> User:
        user = await self._repo.get_by_id(user_id)
        if not user or user.is_deleted:
            raise NotFoundError("User", str(user_id))
        return user

    async def update_user(self, user_id: UUID, data: UserUpdate) -> User:
        user = await self.get_user(user_id)
        updates = data.model_dump(exclude_none=True)
        if not updates:
            return user
        return await self._repo.update(user, **updates)

    async def deactivate_user(self, user_id: UUID) -> User:
        user = await self.get_user(user_id)
        return await self._repo.update(user, is_active=False)

    async def list_users(self, *, limit: int = 100, offset: int = 0) -> list[User]:
        return await self._repo.get_active_users(limit=limit, offset=offset)
