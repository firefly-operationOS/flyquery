#!/usr/bin/env python
# Copyright 2026 Firefly Software Solutions Inc
"""Snapshot the current OpenAPI spec to ``openapi.json`` (repo root).

Invoked by ``task openapi-snapshot``. Imports the FastAPI app, calls
``install_openapi`` (the same function PyFly's lifespan invokes at
startup), clears the cached schema, and writes the regenerated OpenAPI
JSON sorted-keyed for stable diffs.

The drift gate in ``tests/integration/test_openapi_snapshot.py`` runs
the equivalent logic in-process; this script is the convenience entry
point for developers + the CI publish-sdk workflows. Output goes
straight to a file (not stdout) so the ``install_openapi`` log line
(``openapi schema generated (paths=N, schemas=M, tags=K)``) doesn't
pollute the JSON.
"""

from __future__ import annotations

import json
from pathlib import Path

from flyquery import __version__
from flyquery.main import _pyfly, app
from flyquery.web.openapi_override import install_openapi


def main() -> None:
    install_openapi(
        app,
        _pyfly.context,
        title="flyquery",
        version=__version__,
        description="",
    )
    app.openapi_schema = None
    repo_root = Path(__file__).resolve().parent.parent
    target = repo_root / "openapi.json"
    with target.open("w", encoding="utf-8") as f:
        json.dump(app.openapi(), f, indent=2, sort_keys=True)
        f.write("\n")
    print(f"wrote {target} ({target.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
