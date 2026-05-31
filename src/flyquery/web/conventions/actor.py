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

"""Actor resolution from JWT claims or agent token.

The actor is audit metadata, not authorization. It identifies
*who* did the action — never *what* they can do.

JWT signature verification belongs to the API gateway or
upstream IDP integration; the conventions module trusts the
decoded payload it is given.
"""

from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any

_AGENT_PREFIX_LEN = 12  # "agt_" + 8 hex chars


@dataclass(frozen=True)
class Actor:
    value: str  # "user:<sub>" or "agent:<token-prefix>"
    tenant_claim: str | None  # tenant id claimed by the JWT, if any


def actor_from_jwt_claims(claims: dict[str, Any]) -> Actor | None:
    sub = claims.get("sub")
    if not isinstance(sub, str) or not sub:
        return None
    tenant_claim = claims.get("tenant")
    return Actor(
        value=f"user:{sub}",
        tenant_claim=tenant_claim if isinstance(tenant_claim, str) else None,
    )


def actor_from_agent_token(token: str) -> Actor | None:
    if not isinstance(token, str) or len(token) < _AGENT_PREFIX_LEN:
        return None
    prefix = token[:_AGENT_PREFIX_LEN]
    return Actor(value=f"agent:{prefix}", tenant_claim=None)


def decode_jwt_unverified(bearer_value: str) -> dict[str, Any] | None:
    """Decode a JWT payload WITHOUT verifying its signature.

    The conventions module is downstream of the API gateway, which
    is responsible for verification. We just need the claims.
    Returns ``None`` if the header is malformed.
    """
    if not bearer_value.lower().startswith("bearer "):
        return None
    token = bearer_value[len("bearer ") :]
    parts = token.split(".")
    if len(parts) < 2:
        return None
    try:
        payload_b64 = parts[1]
        padding = "=" * (-len(payload_b64) % 4)
        decoded = base64.urlsafe_b64decode(payload_b64 + padding)
        parsed = json.loads(decoded)
        return parsed if isinstance(parsed, dict) else None
    except (ValueError, UnicodeDecodeError):
        return None
