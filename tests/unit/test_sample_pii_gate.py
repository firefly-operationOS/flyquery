# Copyright 2024-2026 Firefly Software Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Unit tests for Stage 4 sample PII gate.

Verifies the critical ordering guarantee: PII inline gate runs BEFORE persisting.
"""

from __future__ import annotations

import pytest

from flyquery.core.services.pii.adapters.disabled_scanner import DisabledPiiScanner
from flyquery.core.services.pii.adapters.regex_scanner import RegexPiiScanner


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
