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

"""PiiScanner Protocol + shared types for flyquery.

Mirrors canon's PII scanner shape (lock-step principle), adapted for
structured-data columns instead of free-text documents.

Three adapters:
  regex      — pattern-based, no extra deps (default)
  presidio   — wraps presidio-analyzer [presidio] extra
  disabled   — always returns None (opt-out workspaces)

Factory: build_pii_scanner(name) — selected by FLYQUERY_PII_SCANNER env.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class PiiFinding:
    """One PII match on a single value."""

    entity_type: str  # "EMAIL", "SSN", "PHONE", "CREDIT_CARD", "IP_ADDRESS", ...
    score: float  # 0..1


@dataclass(frozen=True, slots=True)
class PiiTag:
    """Aggregate tag for a column (post scan_column)."""

    tag: str  # primary entity type or "NONE"
    source: str  # "REGEX" | "PRESIDIO" | "AGENT"


class PiiScanner(Protocol):
    """Detect PII in individual values (scan_single) or full columns (scan_column).

    Both methods are async so adapters can wrap network-bound tools (Presidio
    server mode) without blocking the event loop.
    """

    async def scan_single(self, value: str) -> PiiFinding | None:
        """Return the highest-confidence PII finding for a single value,
        or None if no PII detected."""
        ...

    async def scan_column(
        self,
        name: str,
        description: str | None,
        samples: list[str],
        data_type: str,
    ) -> PiiTag | None:
        """Return a PiiTag for a column (holistic: name + description + samples),
        or None if no PII detected at all."""
        ...
