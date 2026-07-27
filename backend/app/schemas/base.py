"""Shared Pydantic base and common schema utilities."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AppBaseModel(BaseModel):
    """Base model with shared config for all schemas."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


class TimestampSchema(AppBaseModel):
    created_at: datetime
    updated_at: datetime


class IDSchema(AppBaseModel):
    id: UUID
