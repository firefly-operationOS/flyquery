# Copyright 2026 Firefly Software Solutions Inc
"""Disabled PII scanner — always returns None.

Used when FLYQUERY_PII_SCANNER=disabled (workspaces that explicitly opt out
of PII scanning, e.g. fully anonymised datasets in test environments).
"""

from __future__ import annotations

from flyquery.core.services.pii.scanner import PiiFinding, PiiTag


class DisabledPiiScanner:
    """No-op scanner. All methods return None."""

    async def scan_single(self, value: str) -> PiiFinding | None:
        return None

    async def scan_column(
        self,
        name: str,
        description: str | None,
        samples: list[str],
        data_type: str,
    ) -> PiiTag | None:
        return None
