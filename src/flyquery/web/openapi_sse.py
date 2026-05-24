# Copyright 2026 Firefly Software Solutions Inc
"""Declare ``text/event-stream`` for the SSE endpoints in OpenAPI.

Pyfly's ``@get_mapping`` / ``@post_mapping`` decorators don't accept a
``responses`` kwarg, so the generated ``openapi.json`` never tells the
SDK generators that the ``/stream`` endpoints return Server-Sent
Events instead of JSON. The result was:

* Python SDK: ``stream_job`` dumps the raw body (no SSE framing parse).
* Java SDK: ``streamJob`` returns ``Mono<Void>`` because the spec
  declares no response schema.

This module post-processes the spec to attach a proper
``content.text/event-stream`` block to the 200 response of every known
SSE path. SDK regeneration after this enrichment lands produces clients
that can iterate frames (``Flux<ServerSentEvent>`` in Java,
``AsyncIterator[ServerSentEvent]`` in Python).

The enricher is idempotent -- calling it twice is a no-op because it
uses ``setdefault`` at every layer.

A canonical list of SSE endpoints lives in :data:`SSE_ENDPOINTS`. When
a new ``/stream`` endpoint ships, add it here.
"""

from __future__ import annotations

from typing import Any

#: ``(verb, path)`` tuples for every SSE endpoint. Verb is lowercase
#: because OpenAPI's path-item keys are lowercase.
SSE_ENDPOINTS: tuple[tuple[str, str], ...] = (
    ("get", "/api/v1/ingest-jobs/{job_id}/stream"),
    ("post", "/api/v1/query/stream"),
    ("post", "/api/v1/sql:execute/stream"),
    ("post", "/api/v1/agent/query/stream"),
    ("post", "/api/v1/agent/sql:execute/stream"),
)

#: Schema component name registered for the SSE frame envelope. The
#: schema itself is intentionally permissive (a string) -- the wire
#: framing is the canonical SSE format (``event: ...\\ndata: ...\\n\\n``)
#: which SDKs parse via dedicated streaming clients, not via JSON.
SSE_SCHEMA_NAME = "ServerSentEvent"


def _sse_response_block() -> dict[str, Any]:
    """Build the 200-response stanza declaring ``text/event-stream``.

    The ``schema.format`` ``event-stream`` is non-standard but understood
    by openapi-generator's WebClient + asyncio Python templates as a
    hint to emit a streaming response type.
    """
    return {
        "description": (
            "Server-Sent Events stream. Each frame follows the SSE wire "
            "format ``event: <name>\\ndata: <json>\\n\\n``. See "
            "``docs/api-reference.md`` section 8 for the per-endpoint "
            "event catalogue."
        ),
        "content": {
            "text/event-stream": {
                "schema": {
                    "type": "string",
                    "format": "event-stream",
                    "description": (
                        "One SSE frame per event. Frames carry ``event:`` + ``data:`` (JSON-encoded) lines."
                    ),
                }
            }
        },
    }


def enrich_openapi_with_sse(spec: dict[str, Any]) -> None:
    """Mutate ``spec`` in place so every known SSE endpoint declares ``text/event-stream``.

    Idempotent. Unknown endpoints (path not in the spec) are skipped
    silently -- the enricher must survive a partial spec snapshot.

    Parameters
    ----------
    spec:
        The OpenAPI document as returned by FastAPI / pyfly's generator.
    """
    paths = spec.get("paths", {})
    for verb, path in SSE_ENDPOINTS:
        path_item = paths.get(path)
        if not path_item:
            continue
        op = path_item.get(verb)
        if not isinstance(op, dict):
            continue
        responses = op.setdefault("responses", {})
        # Replace any auto-generated 200 stanza -- the default FastAPI
        # one says ``application/json``, which is actively wrong here
        # and would steer SDK generators into wrong output types.
        responses["200"] = _sse_response_block()


__all__ = ["SSE_ENDPOINTS", "SSE_SCHEMA_NAME", "enrich_openapi_with_sse"]
