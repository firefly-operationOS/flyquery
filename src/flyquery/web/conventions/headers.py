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

"""Canonical HTTP-header names used by the firefly wire contract.

Every controller, dependency, and outbound client reads these
constants instead of stringly-typed header names. Renaming a
header thus changes exactly one line.
"""

from __future__ import annotations

HEADER_TENANT_ID = "X-Tenant-Id"
HEADER_WORKSPACE_ID = "X-Workspace-Id"
HEADER_CORRELATION_ID = "X-Correlation-Id"
HEADER_IDEMPOTENCY_KEY = "Idempotency-Key"
HEADER_AGENT_TOKEN = "X-Agent-Token"
HEADER_AUTHORIZATION = "Authorization"
