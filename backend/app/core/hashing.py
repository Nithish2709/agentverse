"""Password hashing utilities using bcrypt via passlib."""

from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


def hash_password(plain: str) -> str:
    """Return bcrypt hash of *plain* password."""
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches *hashed*."""
    return _pwd_context.verify(plain, hashed)


def needs_rehash(hashed: str) -> bool:
    """Return True if the hash should be upgraded (e.g. rounds changed)."""
    return _pwd_context.needs_update(hashed)
