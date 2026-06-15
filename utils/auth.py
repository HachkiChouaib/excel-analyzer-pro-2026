"""Lightweight authentication layer.

Users are persisted in a JSON file with passwords stored as salted PBKDF2
hashes (never in plain text). This module is UI-agnostic so it can be unit
tested without Streamlit.

Note:
    This is a portfolio-grade implementation. For a real production system,
    prefer a proper database and a battle-tested auth library / identity
    provider.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from utils.helpers import DATA_DIR, ensure_directories

USERS_FILE: Path = DATA_DIR / "users.json"

# PBKDF2 parameters.
_ALGORITHM = "sha256"
_ITERATIONS = 200_000
_SALT_BYTES = 16


@dataclass(frozen=True)
class AuthResult:
    """Outcome of an authentication or registration attempt.

    Attributes:
        success: Whether the operation succeeded.
        message: A human-readable status message.
    """

    success: bool
    message: str


def _hash_password(password: str, salt: bytes) -> str:
    """Return the hex PBKDF2 hash of ``password`` using ``salt``."""
    derived = hashlib.pbkdf2_hmac(
        _ALGORITHM, password.encode("utf-8"), salt, _ITERATIONS
    )
    return derived.hex()


def _load_users() -> dict[str, dict[str, Any]]:
    """Load the user store from disk, returning an empty dict if absent."""
    if not USERS_FILE.exists():
        return {}
    try:
        with USERS_FILE.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _save_users(users: dict[str, dict[str, Any]]) -> None:
    """Persist the user store to disk."""
    ensure_directories()
    with USERS_FILE.open("w", encoding="utf-8") as fh:
        json.dump(users, fh, ensure_ascii=False, indent=2)


def register_user(username: str, password: str) -> AuthResult:
    """Register a new user.

    Args:
        username: Desired username (case-insensitive, trimmed).
        password: Plain-text password (min. 6 characters).

    Returns:
        An :class:`AuthResult` describing the outcome.
    """
    username = username.strip().lower()
    if not username:
        return AuthResult(False, "Username cannot be empty.")
    if len(password) < 6:
        return AuthResult(False, "Password must be at least 6 characters long.")

    users = _load_users()
    if username in users:
        return AuthResult(False, "This username is already taken.")

    salt = os.urandom(_SALT_BYTES)
    users[username] = {
        "salt": salt.hex(),
        "hash": _hash_password(password, salt),
    }
    _save_users(users)
    return AuthResult(True, "Account created successfully. You can now log in.")


def authenticate(username: str, password: str) -> AuthResult:
    """Verify a username/password pair.

    Args:
        username: The username to check (case-insensitive).
        password: The plain-text password to verify.

    Returns:
        An :class:`AuthResult` describing the outcome.
    """
    username = username.strip().lower()
    users = _load_users()
    record = users.get(username)
    if record is None:
        return AuthResult(False, "Invalid username or password.")

    salt = bytes.fromhex(record["salt"])
    candidate = _hash_password(password, salt)
    # Constant-time comparison to avoid timing attacks.
    if hmac.compare_digest(candidate, record["hash"]):
        return AuthResult(True, "Login successful.")
    return AuthResult(False, "Invalid username or password.")


def user_exists(username: str) -> bool:
    """Return ``True`` if a user with the given name exists."""
    return username.strip().lower() in _load_users()
