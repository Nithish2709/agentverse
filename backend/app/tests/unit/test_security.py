"""Unit tests for security utilities."""

import pytest
from datetime import UTC, datetime, timedelta

from app.core.hashing import hash_password, needs_rehash, verify_password
from app.core.security import (
    Permission,
    Role,
    create_access_token,
    create_token_pair,
    decode_token,
    get_permissions_for_role,
)
from app.core.exceptions import AuthenticationError


class TestPasswordHashing:
    def test_hash_is_not_plaintext(self):
        assert hash_password("Secret1") != "Secret1"

    def test_verify_correct_password(self):
        hashed = hash_password("Secret1")
        assert verify_password("Secret1", hashed) is True

    def test_reject_wrong_password(self):
        hashed = hash_password("Secret1")
        assert verify_password("Wrong1", hashed) is False

    def test_needs_rehash_returns_bool(self):
        hashed = hash_password("Secret1")
        assert isinstance(needs_rehash(hashed), bool)


class TestRBAC:
    def test_super_admin_has_all_permissions(self):
        perms = get_permissions_for_role(Role.SUPER_ADMIN)
        assert set(Permission).issubset(perms)

    def test_viewer_cannot_write_users(self):
        perms = get_permissions_for_role(Role.VIEWER)
        assert Permission.USER_WRITE not in perms

    def test_analyst_can_read_reports(self):
        perms = get_permissions_for_role(Role.ANALYST)
        assert Permission.REPORT_READ in perms


class TestJWT:
    def test_create_and_decode_access_token(self, monkeypatch):
        import os
        monkeypatch.setenv("SECRET_KEY", "a" * 32)
        monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost/db")
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")

        from app.config.settings import Settings
        from app.config import get_settings
        get_settings.cache_clear()

        token = create_access_token("user-123", Role.ANALYST)
        payload = decode_token(token)

        assert payload.sub == "user-123"
        assert payload.role == Role.ANALYST
        assert Permission.REPORT_READ in payload.permissions

    def test_invalid_token_raises(self):
        with pytest.raises(AuthenticationError):
            decode_token("not.a.valid.token")
