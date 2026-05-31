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

"""Lifecycle response envelopes shared across resources.

Currently exposes :class:`PurgeAccepted` -- the 202 response shape for
hard-delete endpoints (``DELETE /datasets/{id}:purge``, future
``/agent-tokens/{id}:rotate``, etc.). Workspaces also use a purge
endpoint but its controller is byte-equivalent with canon / radar
(lock-step) and ships a bare dict; new endpoints introduced by flyquery
should use this typed envelope instead.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class PurgeAccepted(BaseModel):
    """202 Accepted envelope for purge-style endpoints.

    ``status`` is always ``"accepted"`` (mirrors the workspaces purge
    contract). ``tombstone_expires_at`` is a human-readable hint --
    consumers receive an ISO-8601 timestamp when the retention job
    actually deletes the SQL row; today the value is the ``+90d``
    placeholder (90 days mirrors ``conv_ttl_days``).
    """

    model_config = ConfigDict(frozen=True)

    status: str = Field(default="accepted", description="Always 'accepted' for 202 responses.")
    tombstone_expires_at: str = Field(
        description=(
            "When the SQL row is expected to be hard-deleted. ISO-8601 once a "
            "retention job is wired; today returns a coarse hint such as '+90d'."
        )
    )


__all__ = ["PurgeAccepted"]
