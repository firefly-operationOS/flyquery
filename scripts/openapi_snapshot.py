#!/usr/bin/env python
# Copyright 2026 Firefly Software Solutions Inc
"""Snapshot the current OpenAPI spec to stdout.

Invoked by ``task openapi-snapshot``. Imports the FastAPI app, calls
``install_openapi`` (the same function PyFly's lifespan invokes at
startup), clears the cached schema, and prints the regenerated OpenAPI
JSON sorted-keyed for stable diffs.

The drift gate in ``tests/integration/test_openapi_snapshot.py`` runs
the equivalent logic in-process; this script is the convenience entry
point for developers + the CI publish-sdk workflows.
"""

from __future__ import annotations

import json

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
    print(json.dumps(app.openapi(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
