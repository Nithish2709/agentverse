"""Alembic environment — wires async SQLAlchemy engine to migration runner."""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

# Import Base and all models so Alembic can detect schema changes
from app.config import get_settings
from app.database.session import Base
import app.models  # noqa: F401 — registers all ORM models

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _get_url() -> str:
    url = get_settings().database_url_str
    return url.replace("postgresql://", "postgresql+asyncpg://", 1).replace(
        "postgres://", "postgresql+asyncpg://", 1
    )


def run_migrations_offline() -> None:
    context.configure(
        url=_get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    engine = create_async_engine(_get_url(), future=True)
    async with engine.connect() as conn:
        await conn.run_sync(
            lambda sync_conn: context.configure(
                connection=sync_conn,
                target_metadata=target_metadata,
                compare_type=True,
            )
        )
        async with conn.begin():
            await conn.run_sync(lambda _: context.run_migrations())
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
