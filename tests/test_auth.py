"""Unit tests for :mod:`utils.auth`.

The user store path is redirected to a temporary directory so tests never
touch the real ``data/users.json``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from utils import auth


@pytest.fixture(autouse=True)
def temp_user_store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Redirect the user store to a temporary file for each test."""
    monkeypatch.setattr(auth, "USERS_FILE", tmp_path / "users.json")


def test_register_and_authenticate() -> None:
    assert auth.register_user("Alice", "secret123").success
    assert auth.authenticate("alice", "secret123").success


def test_register_duplicate_fails() -> None:
    auth.register_user("bob", "secret123")
    result = auth.register_user("bob", "another1")
    assert not result.success
    assert "taken" in result.message.lower()


def test_register_short_password_fails() -> None:
    result = auth.register_user("carol", "123")
    assert not result.success


def test_authenticate_wrong_password() -> None:
    auth.register_user("dave", "secret123")
    assert not auth.authenticate("dave", "wrongpass").success


def test_authenticate_unknown_user() -> None:
    assert not auth.authenticate("ghost", "whatever").success


def test_username_is_case_insensitive() -> None:
    auth.register_user("Eve", "secret123")
    assert auth.authenticate("EVE", "secret123").success
    assert auth.user_exists("eve")


def test_password_is_not_stored_in_plaintext(tmp_path: Path) -> None:
    auth.register_user("frank", "supersecret")
    stored = (tmp_path / "users.json").read_text(encoding="utf-8")
    assert "supersecret" not in stored
