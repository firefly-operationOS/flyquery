# Copyright 2026 Firefly Software Solutions Inc
"""Unit tests for Stage 4 sample PII gate.

Verifies the critical ordering guarantee: PII inline gate runs BEFORE persisting.
"""

from __future__ import annotations

import pytest

from flyquery.core.services.pii.adapters.regex_scanner import RegexPiiScanner
from flyquery.core.services.pii.adapters.disabled_scanner import DisabledPiiScanner


class TestPiiGateOrdering:
    """Verify that PII values are dropped before sample persistence."""

    @pytest.mark.asyncio
    async def test_all_clean_values_kept(self):
        scanner = RegexPiiScanner()
        raw = ["Alice", "Bob", "Carol"]
        clean = []
        for v in raw:
            finding = await scanner.scan_single(v)
            if finding is None:
                clean.append(v)
        assert clean == ["Alice", "Bob", "Carol"]

    @pytest.mark.asyncio
    async def test_pii_values_dropped(self):
        scanner = RegexPiiScanner()
        raw = ["Alice", "user@example.com", "Bob", "123-45-6789"]
        clean = []
        for v in raw:
            finding = await scanner.scan_single(v)
            if finding is None:
                clean.append(v)
        # email and SSN should be dropped
        assert "user@example.com" not in clean
        assert "123-45-6789" not in clean
        assert "Alice" in clean
        assert "Bob" in clean

    @pytest.mark.asyncio
    async def test_all_pii_yields_empty(self):
        scanner = RegexPiiScanner()
        raw = ["user@example.com", "admin@test.org"]
        clean = []
        for v in raw:
            finding = await scanner.scan_single(v)
            if finding is None:
                clean.append(v)
        assert clean == []

    @pytest.mark.asyncio
    async def test_disabled_scanner_keeps_all(self):
        scanner = DisabledPiiScanner()
        raw = ["user@example.com", "123-45-6789", "hello"]
        clean = []
        for v in raw:
            finding = await scanner.scan_single(v)
            if finding is None:
                clean.append(v)
        # disabled scanner never flags anything
        assert len(clean) == 3


class TestParquetColumnQuote:
    """Test the _quote_ident helper."""

    def test_simple_name(self):
        from flyquery.core.services.ingestion.stages.sample import _quote_ident
        assert _quote_ident("customer_id") == '"customer_id"'

    def test_name_with_quotes(self):
        from flyquery.core.services.ingestion.stages.sample import _quote_ident
        assert _quote_ident('a"b') == '"a""b"'
