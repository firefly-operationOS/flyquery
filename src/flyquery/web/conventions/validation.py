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

"""Slug validation for tenant_id / workspace_id header values."""

from __future__ import annotations

import re

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


class InvalidSlugError(ValueError):
    """Raised when a slug fails the firefly charset.

    Carries the offending value (and *only* the value, not user PII)
    so callers can log a redacted error without leaking the rest of
    the request context.
    """

    def __init__(self, value: str) -> None:
        super().__init__(f"invalid slug: {value!r}")
        self.value = value


def validate_slug(value: str) -> str:
    """Return ``value`` unchanged if it matches the slug grammar.

    Slug grammar: ``^[a-z0-9][a-z0-9_-]{0,63}$`` — 1-64 chars,
    starts alphanumeric, lowercase ASCII + digits + ``_`` + ``-``.
    """
    if not isinstance(value, str) or not _SLUG_RE.fullmatch(value):
        raise InvalidSlugError(value if isinstance(value, str) else "")
    return value
