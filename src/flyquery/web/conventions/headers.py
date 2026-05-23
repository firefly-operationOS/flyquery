# Copyright 2026 Firefly Software Solutions Inc
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
