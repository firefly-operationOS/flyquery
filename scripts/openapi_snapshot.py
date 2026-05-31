#!/usr/bin/env python
# Copyright 2026 Firefly Software Solutions Inc
"""Snapshot the current OpenAPI spec to ``openapi.json`` (repo root).

Invoked by ``task openapi-snapshot``. Imports the FastAPI app -- which
in turn installs pyfly's OpenAPI generator AND wraps it in
``_wrapped_openapi`` so every call layers flyquery's header + security
surface on top -- clears the cached schema, and writes the regenerated
OpenAPI JSON sorted-keyed for stable diffs.

The drift gate in ``tests/integration/test_openapi_snapshot.py`` runs
the equivalent logic in-process; this script is the convenience entry
point for developers + the CI publish-sdk workflows. Output goes
straight to a file (not stdout) so the ``install_openapi`` log line
(``openapi schema generated (paths=N, schemas=M, tags=K)``) doesn't
pollute the JSON.

This script must NOT re-invoke ``install_openapi``: that re-binds
``app.openapi`` to pyfly's bare generator and discards the
``_wrapped_openapi`` shim installed by ``flyquery.main``, dropping every
``X-Tenant-Id`` / ``X-Workspace-Id`` / ``X-Agent-Token`` /
``Idempotency-Key`` parameter and every ``securityScheme`` from the spec
(generated SDKs then can't enforce the four-header contract). It relies
on the wrapping ``flyquery.main`` installs at import, and defensively
re-runs ``enrich_openapi_with_headers`` on the dumped spec so the
snapshot stays correct regardless of how ``main.py`` evolves.
"""

from __future__ import annotations

import json
from pathlib import Path

from flyquery.main import app
from flyquery.web.openapi_headers import enrich_openapi_with_headers
from flyquery.web.openapi_sse import enrich_openapi_with_sse


def main() -> None:
    # Importing ``flyquery.main`` already ran ``install_openapi(app, ...)``
    # and bound ``_wrapped_openapi``; clearing the cache forces a fresh
    # build through the wrapper.
    app.openapi_schema = None
    spec = app.openapi()
    # Defensive double-apply: both enrichers are idempotent (``setdefault``
    # everywhere for headers, replace-only-the-200 for SSE), so re-running
    # them here guarantees the snapshot ships the header + security +
    # SSE response surface even if ``flyquery.main`` is later refactored.
    enrich_openapi_with_headers(spec)
    enrich_openapi_with_sse(spec)

    repo_root = Path(__file__).resolve().parent.parent
    target = repo_root / "openapi.json"
    with target.open("w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, sort_keys=True)
        f.write("\n")
    print(f"wrote {target} ({target.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
