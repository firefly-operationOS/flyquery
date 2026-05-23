# Copyright 2026 Firefly Software Solutions Inc
"""Shared pytest fixtures for flyquery tests."""

from __future__ import annotations

import os

import pytest


@pytest.fixture(autouse=True)
def reset_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default to disabled migrations and an in-memory SQLite KB for unit tests."""
    monkeypatch.setenv("FLYQUERY_RUN_MIGRATIONS", "false")
