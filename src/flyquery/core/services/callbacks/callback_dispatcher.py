# Copyright 2026 Firefly Software Solutions Inc
"""HMAC-signed HTTP POST -- the single seam used by the callback worker.

Kept as a pure function so it's trivially unit-testable; the worker
loop pulls due rows + calls :func:`deliver` per row + persists the
outcome via :class:`CallbackOutboxRepository`.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from dataclasses import dataclass
from typing import Any

import httpx

_USER_AGENT = "flyquery-callback/26"


@dataclass(slots=True)
class DeliveryOutcome:
    """One-shot HTTP attempt result."""

    success: bool  # 2xx
    status_code: int | None
    error: str | None  # only set on failure


def sign_body(secret: str, body: bytes) -> str:
    """Return the ``X-Flyquery-Signature`` header value for ``body``."""
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


async def deliver(
    *,
    client: httpx.AsyncClient,
    url: str,
    payload: dict[str, Any],
    secret: str | None,
    extra_headers: dict[str, str],
    event_type: str,
    ingest_job_id: uuid.UUID,
    timeout_s: float,
) -> DeliveryOutcome:
    """POST ``payload`` (as JSON) to ``url`` with HMAC signature when ``secret`` is set.

    Returns a :class:`DeliveryOutcome` describing the attempt. The
    caller decides retry vs terminal-fail based on the outcome plus
    the current ``attempts`` count.

    Any 2xx response counts as success (including 200, 201, 202, 204).
    A transport error (DNS, TLS, connection-refused, read-timeout)
    has ``status_code=None``.
    """
    body = json.dumps(payload, default=_json_default).encode("utf-8")
    # ORDER MATTERS: apply caller-supplied extras FIRST, then overwrite
    # with our reserved keys so a misconfigured / malicious caller
    # can't shadow ``X-Flyquery-Signature`` (or Content-Type, etc.).
    # The CallbackConfig DTO already rejects reserved keys on the
    # request path, but the process-wide default headers bypass that
    # DTO -- this guard catches both surfaces.
    headers: dict[str, str] = {}
    headers.update(extra_headers or {})
    headers["Content-Type"] = "application/json"
    headers["User-Agent"] = _USER_AGENT
    headers["X-Flyquery-Event"] = event_type
    headers["X-Flyquery-Job-Id"] = str(ingest_job_id)
    if secret:
        headers["X-Flyquery-Signature"] = sign_body(secret, body)

    try:
        response = await client.post(url, content=body, headers=headers, timeout=timeout_s)
    except httpx.HTTPError as exc:
        return DeliveryOutcome(success=False, status_code=None, error=f"transport: {exc!r}")

    if 200 <= response.status_code < 300:
        return DeliveryOutcome(success=True, status_code=response.status_code, error=None)
    return DeliveryOutcome(
        success=False,
        status_code=response.status_code,
        error=f"http {response.status_code}: {response.text[:200]!r}",
    )


def _json_default(o: Any) -> Any:
    if isinstance(o, uuid.UUID):
        return str(o)
    return str(o)
