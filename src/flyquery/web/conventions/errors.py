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

"""``ProblemDetail`` -- RFC 7807 envelope (with separate code field).

Authoritative wire shape for every error response: ``code`` is the
machine-readable snake_case identifier consumers branch on; ``title``
is the human-readable label. Superseded the title-as-code DTO in
``flyradar.interfaces.dtos.error`` (deleted alongside the legacy
``flyradar.web.advice`` package).
"""

from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

_CODE_RE = re.compile(r"^[a-z][a-z0-9_]{0,63}$")


class ProblemDetail(BaseModel):
    """RFC 7807 problem-detail used by the firefly wire contract.

    - ``type``: canonical URI (stable doc anchor).
    - ``code``: machine-readable snake_case identifier consumers
      branch on.
    - ``title``: short human-readable label.
    - ``errors``: per-field validation issues as ``{code, path,
      message}`` triples.
    """

    model_config = ConfigDict(frozen=True)

    type: str
    code: str
    title: str
    status: int = Field(ge=100, le=599)
    detail: str | None = None
    instance: str | None = None
    correlation_id: str | None = None
    errors: list[dict[str, Any]] = Field(default_factory=list)

    @field_validator("code")
    @classmethod
    def _code_shape(cls, value: str) -> str:
        if not _CODE_RE.fullmatch(value):
            raise ValueError(f"code must be snake_case ASCII, got {value!r}")
        return value
