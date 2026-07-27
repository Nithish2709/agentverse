"""Models package — imports all ORM models so Alembic can discover them."""

from app.models.user import User

__all__ = ["User"]
