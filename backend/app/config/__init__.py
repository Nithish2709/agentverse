"""Config package — exposes settings singleton."""

from app.config.settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]
