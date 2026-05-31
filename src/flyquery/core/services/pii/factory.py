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

"""PiiScanner factory — resolves adapter from FLYQUERY_PII_SCANNER env.

Recognised values:
    regex     — default; pattern-based, no extra deps
    presidio  — wraps presidio-analyzer [presidio] extra (fails loudly if missing)
    disabled  — always returns None (explicit opt-out)

Unknown values fall back to the regex scanner (same as canon) so a typo
never silently disables PII detection.
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def build_pii_scanner(name: str | None = None):
    """Return the appropriate PiiScanner instance for the given name.

    Args:
        name: Value of FLYQUERY_PII_SCANNER env var (or None → default "regex").
    """
    key = (name or "regex").strip().lower()

    if key == "disabled":
        from flyquery.core.services.pii.adapters.disabled_scanner import DisabledPiiScanner

        return DisabledPiiScanner()

    if key == "presidio":
        from flyquery.core.services.pii.adapters.presidio_scanner import PresidioPiiScanner

        return PresidioPiiScanner()  # ImportError raised here if extra missing

    if key != "regex":
        logger.warning("unknown FLYQUERY_PII_SCANNER=%r — falling back to regex scanner", name)

    from flyquery.core.services.pii.adapters.regex_scanner import RegexPiiScanner

    return RegexPiiScanner()
