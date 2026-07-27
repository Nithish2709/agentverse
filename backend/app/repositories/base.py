"""Generic async repository base — implements the Repository Pattern."""

from typing import Any, Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """CRUD operations for a single SQLAlchemy model."""

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, id: UUID) -> ModelT | None:
        return await self._session.get(self.model, id)

    async def get_all(self, *, limit: int = 100, offset: int = 0) -> list[ModelT]:
        result = await self._session.execute(
            select(self.model).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def create(self, **kwargs: Any) -> ModelT:
        instance = self.model(**kwargs)
        self._session.add(instance)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def update(self, instance: ModelT, **kwargs: Any) -> ModelT:
        for key, value in kwargs.items():
            setattr(instance, key, value)
        await self._session.flush()
        await self._session.refresh(instance)
        return instance

    async def delete(self, instance: ModelT) -> None:
        await self._session.delete(instance)
        await self._session.flush()

    async def count(self) -> int:
        from sqlalchemy import func
        result = await self._session.execute(
            select(func.count()).select_from(self.model)
        )
        return result.scalar_one()
