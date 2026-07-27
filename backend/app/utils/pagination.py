"""Pagination utility shared across list endpoints."""

from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    limit: int = Field(default=20, ge=1, le=200)
    offset: int = Field(default=0, ge=0)


class PaginatedResponse[T](BaseModel):
    items: list[T]
    total: int
    limit: int
    offset: int

    @property
    def has_more(self) -> bool:
        return self.offset + self.limit < self.total
