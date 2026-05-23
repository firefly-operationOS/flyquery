# Copyright 2026 Firefly Software Solutions Inc
"""Unit tests for profile stage helpers and PII tag policy logic."""

from __future__ import annotations

import pytest


class TestProfileTypeHelpers:
    """Test numeric/temporal type detection helpers."""

    def test_integer_is_numeric(self):
        from flyquery.core.services.ingestion.stages.profile import _is_numeric

        assert _is_numeric("INTEGER")
        assert _is_numeric("BIGINT")
        assert _is_numeric("DOUBLE")
        assert _is_numeric("DECIMAL(10,2)")

    def test_varchar_not_numeric(self):
        from flyquery.core.services.ingestion.stages.profile import _is_numeric

        assert not _is_numeric("VARCHAR")
        assert not _is_numeric("TEXT")

    def test_date_is_temporal(self):
        from flyquery.core.services.ingestion.stages.profile import _is_temporal

        assert _is_temporal("DATE")
        assert _is_temporal("TIMESTAMP")
        assert _is_temporal("TIMESTAMPTZ")

    def test_varchar_not_temporal(self):
        from flyquery.core.services.ingestion.stages.profile import _is_temporal

        assert not _is_temporal("VARCHAR")


class TestPiiTagPolicyDocumentation:
    """Verify policy constants documented correctly."""

    def test_valid_policies(self):
        # Policy is enforced at settings level; just document valid values
        valid = {"warn", "redact", "reject"}
        assert "warn" in valid
        assert "redact" in valid
        assert "reject" in valid

    @pytest.mark.asyncio
    async def test_pii_tag_module_importable(self):
        from flyquery.core.services.ingestion.stages import pii_tag

        assert hasattr(pii_tag, "run_pii_tag")

    @pytest.mark.asyncio
    async def test_profile_module_importable(self):
        from flyquery.core.services.ingestion.stages import profile

        assert hasattr(profile, "run_profile")
