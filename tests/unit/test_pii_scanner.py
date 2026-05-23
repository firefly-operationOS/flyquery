# Copyright 2026 Firefly Software Solutions Inc
"""Unit tests for the PII scanner port + regex adapter."""

from __future__ import annotations

import pytest

from flyquery.core.services.pii.adapters.regex_scanner import RegexPiiScanner
from flyquery.core.services.pii.adapters.disabled_scanner import DisabledPiiScanner
from flyquery.core.services.pii.factory import build_pii_scanner


# ---------------------------------------------------------------------------
# scan_single
# ---------------------------------------------------------------------------

class TestRegexScannerScanSingle:
    @pytest.mark.asyncio
    async def test_detects_email(self):
        s = RegexPiiScanner()
        finding = await s.scan_single("user@example.com")
        assert finding is not None
        assert finding.entity_type == "EMAIL"

    @pytest.mark.asyncio
    async def test_detects_ssn(self):
        s = RegexPiiScanner()
        finding = await s.scan_single("123-45-6789")
        assert finding is not None
        assert finding.entity_type == "SSN"

    @pytest.mark.asyncio
    async def test_detects_ipv4(self):
        s = RegexPiiScanner()
        finding = await s.scan_single("192.168.1.100")
        assert finding is not None
        assert finding.entity_type == "IP_ADDRESS"

    @pytest.mark.asyncio
    async def test_detects_credit_card(self):
        s = RegexPiiScanner()
        finding = await s.scan_single("4111 1111 1111 1111")
        assert finding is not None
        assert finding.entity_type == "CREDIT_CARD"

    @pytest.mark.asyncio
    async def test_clean_value_returns_none(self):
        s = RegexPiiScanner()
        finding = await s.scan_single("hello world")
        assert finding is None

    @pytest.mark.asyncio
    async def test_plain_number_returns_none(self):
        s = RegexPiiScanner()
        finding = await s.scan_single("42")
        assert finding is None

    @pytest.mark.asyncio
    async def test_empty_string_returns_none(self):
        s = RegexPiiScanner()
        finding = await s.scan_single("")
        assert finding is None


# ---------------------------------------------------------------------------
# scan_column
# ---------------------------------------------------------------------------

class TestRegexScannerScanColumn:
    @pytest.mark.asyncio
    async def test_email_column_name_hint(self):
        s = RegexPiiScanner()
        tag = await s.scan_column("email", None, ["alice@example.com"], "VARCHAR")
        assert tag is not None
        assert tag.tag == "EMAIL"
        assert tag.source == "REGEX"

    @pytest.mark.asyncio
    async def test_phone_column_name_hint(self):
        s = RegexPiiScanner()
        tag = await s.scan_column("phone_number", None, ["555-1234"], "VARCHAR")
        assert tag is not None
        assert tag.tag == "PHONE"

    @pytest.mark.asyncio
    async def test_detects_via_samples(self):
        s = RegexPiiScanner()
        tag = await s.scan_column("contact", None, ["user@example.com", "test@test.org"], "VARCHAR")
        assert tag is not None
        assert tag.tag == "EMAIL"

    @pytest.mark.asyncio
    async def test_clean_column_returns_none(self):
        s = RegexPiiScanner()
        tag = await s.scan_column("order_id", None, ["1001", "1002", "1003"], "INTEGER")
        assert tag is None

    @pytest.mark.asyncio
    async def test_description_hint(self):
        s = RegexPiiScanner()
        tag = await s.scan_column("col_a", "contains email addresses", [], "VARCHAR")
        assert tag is not None
        assert tag.tag == "EMAIL"


# ---------------------------------------------------------------------------
# Disabled scanner
# ---------------------------------------------------------------------------

class TestDisabledScanner:
    @pytest.mark.asyncio
    async def test_scan_single_always_none(self):
        s = DisabledPiiScanner()
        assert await s.scan_single("user@example.com") is None

    @pytest.mark.asyncio
    async def test_scan_column_always_none(self):
        s = DisabledPiiScanner()
        assert await s.scan_column("email", None, ["user@example.com"], "VARCHAR") is None


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

class TestPiiScannerFactory:
    def test_regex_returns_regex_scanner(self):
        scanner = build_pii_scanner("regex")
        assert scanner.__class__.__name__ == "RegexPiiScanner"

    def test_none_defaults_to_regex(self):
        scanner = build_pii_scanner(None)
        assert scanner.__class__.__name__ == "RegexPiiScanner"

    def test_disabled_returns_disabled_scanner(self):
        scanner = build_pii_scanner("disabled")
        assert scanner.__class__.__name__ == "DisabledPiiScanner"

    def test_unknown_falls_back_to_regex(self):
        scanner = build_pii_scanner("unknown_adapter")
        assert scanner.__class__.__name__ == "RegexPiiScanner"
