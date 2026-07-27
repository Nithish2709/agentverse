"""User repository — data access layer for the User model."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(User).where(User.email == email, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        result = await self._session.execute(
            select(User).where(User.username == username, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_active_users(self, *, limit: int = 100, offset: int = 0) -> list[User]:
        result = await self._session.execute(
            select(User)
            .where(User.is_active.is_(True), User.deleted_at.is_(None))
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())
