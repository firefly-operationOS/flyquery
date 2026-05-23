#!/usr/bin/env python
# Copyright 2026 Firefly Software Solutions Inc
"""Lock-step CI gate (spec §14).

Computes the SHA-256 of each lock-step file (after a deterministic
service-name de-substitution: replaces 'flyquery' -> 'flycanon',
'FLYQUERY' -> 'FLYCANON', etc. — same regex set as the copy
script in Tasks 10-11) and compares against the pinned canon SHA in
scripts/lockstep_pins.json.

Drift = exit code 1. Pinned SHAs are refreshed when an intentional
canon-side change lands and we propagate it across canon/radar/flyquery
in lock-step (rare).
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


LOCKSTEP_FILES = [
    "src/flyquery/web/agent_deps.py",
    "src/flyquery/web/openapi_override.py",
    "src/flyquery/web/conventions/__init__.py",
    "src/flyquery/web/conventions/actor.py",
    "src/flyquery/web/conventions/context.py",
    "src/flyquery/web/conventions/db.py",
    "src/flyquery/web/conventions/deps.py",
    "src/flyquery/web/conventions/errors.py",
    "src/flyquery/web/conventions/exceptions.py",
    "src/flyquery/web/conventions/handlers.py",
    "src/flyquery/web/conventions/headers.py",
    "src/flyquery/web/conventions/http_client.py",
    "src/flyquery/web/conventions/idempotency.py",
    "src/flyquery/web/conventions/middleware.py",
    "src/flyquery/web/conventions/redis_idempotency.py",
    "src/flyquery/web/conventions/validation.py",
    "src/flyquery/core/agents/builder.py",
    "src/flyquery/core/observability/__init__.py",
    "src/flyquery/core/services/auth/agent_token_service.py",
    "src/flyquery/core/services/auth/redis_rate_limiter.py",
    "src/flyquery/web/controllers/agent_tokens_controller.py",
]


def _normalise(text: str) -> bytes:
    """Reverse the flyquery substitutions to canon's form, so the SHA is
    canon-pinned regardless of which service we're checking."""
    text = re.sub(r"\bflyquery\b", "flycanon", text)
    text = re.sub(r"\bFLYQUERY\b", "FLYCANON", text)
    text = re.sub(r"\bflyquery_", "canon_", text)
    text = re.sub(r"\bFlyquerySettings\b", "CanonSettings", text)
    return text.encode("utf-8")


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    pins_path = root / "scripts" / "lockstep_pins.json"
    pins: dict[str, str] = json.loads(pins_path.read_text()) if pins_path.exists() else {}
    drift: list[str] = []
    for rel in LOCKSTEP_FILES:
        p = root / rel
        if not p.exists():
            drift.append(f"MISSING: {rel}")
            continue
        sha = hashlib.sha256(_normalise(p.read_text())).hexdigest()
        pinned = pins.get(rel)
        if pinned is None:
            drift.append(f"UNPINNED: {rel} -> {sha}")
        elif pinned != sha:
            drift.append(f"DRIFT: {rel}\n    pinned:  {pinned}\n    current: {sha}")
    if drift:
        print("\n".join(drift))
        return 1
    print(f"lockstep OK: {len(LOCKSTEP_FILES)} files match pins")
    return 0


if __name__ == "__main__":
    sys.exit(main())
