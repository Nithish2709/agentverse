"""Datetime helpers."""

from datetime import UTC, datetime


def utcnow() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(UTC)


def to_utc(dt: datetime) -> datetime:
    """Ensure *dt* is UTC-aware."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)
