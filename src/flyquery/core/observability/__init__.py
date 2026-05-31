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

"""Observability primitives shared across every pipeline stage.

* :func:`timed_agent_run` -- async context manager that records the
  per-stage latency and propagates the W3C correlation context into
  the agent's structured logs.
* :data:`DEFAULT_MIDDLEWARE` -- the agentic middleware stack every
  ``FireflyAgent`` is built with: usage tracking, logging,
  prompt-cache, validation. The orchestrator's RetryMiddleware lives
  separately so a stage can opt out (e.g. the deterministic ones).
* :func:`log_outbound` -- thin wrapper around :func:`structlog.get_logger`
  to emit the ``outbound_call`` line for every LLM / webhook call.
"""

from __future__ import annotations

import logging
import os
import time
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from typing import Any

from fireflyframework_agentic.agents.builtin_middleware import (
    LoggingMiddleware,
    ObservabilityMiddleware,
    ValidationMiddleware,  # noqa: F401 -- referenced from the module docstring as an extension point
)
from fireflyframework_agentic.agents.middleware import AgentMiddleware
from fireflyframework_agentic.agents.prompt_cache import PromptCacheMiddleware

logger = logging.getLogger(__name__)


def _prompt_cache_enabled() -> bool:
    """Read ``FLYQUERY_PROMPT_CACHE`` and decide if caching is on.

    Default ``"on"``. Set to ``"off"`` / ``"0"`` / ``"false"`` to skip
    attaching the middleware (handy for A/B benchmarking and disaster
    rollback). Case-insensitive.
    """
    raw = os.environ.get("FLYQUERY_PROMPT_CACHE", "on").strip().lower()
    return raw not in {"off", "0", "false", "no"}


#: Anthropic prompt-cache middleware -- single shared instance reused
#: by every service so the cache settings stay consistent (same TTL,
#: same blocks marked). System prompts are massive and identical
#: across the dozens of LLM calls per discovery, so this is the
#: cheapest, highest-leverage cost optimisation we have.
PROMPT_CACHE_MIDDLEWARE = PromptCacheMiddleware(
    cache_system_prompt=True,
    cache_last_message=True,
    cache_ttl_seconds=300,
    enabled=_prompt_cache_enabled(),
)


DEFAULT_MIDDLEWARE: Sequence[AgentMiddleware] = (
    PROMPT_CACHE_MIDDLEWARE,
    LoggingMiddleware(),
    ObservabilityMiddleware(),
)
"""Middleware stack applied to every :class:`FireflyAgent` constructed
by an intelligence stage. Listed in execution order: outermost first.

Stages that want bespoke middleware (e.g. a hard cost-cap on the
duplicity detector, output validation via
:class:`ValidationMiddleware` with a tenant-specific reviewer)
append to this tuple instead of replacing it, so the baseline
behaviour stays consistent.
"""


@asynccontextmanager
async def timed_agent_run(stage: str, **extra: Any) -> AsyncIterator[dict[str, Any]]:
    """Context manager recording latency of a stage's agent call.

    Yields a dictionary the caller can populate with extra fields
    (token counts, agent name, model used). On exit the manager emits
    a single structured ``stage_completed`` log line with the latency
    and every populated field -- one log entry per stage call.
    """
    started = time.monotonic()
    context: dict[str, Any] = {"stage": stage, **extra}
    try:
        yield context
        context["status"] = context.get("status", "success")
    except Exception as exc:  # noqa: BLE001 - we re-raise after logging
        context["status"] = "failed"
        context["error"] = str(exc)
        raise
    finally:
        context["latency_ms"] = int((time.monotonic() - started) * 1000)
        logger.info("stage_completed", extra=context)


def log_outbound(
    *,
    kind: str,
    target: str,
    duration_ms: int,
    cost_usd: float | None = None,
    status: str = "success",
    **extra: Any,
) -> None:
    """Emit a structured ``outbound_call`` log entry.

    Used for every LLM call, webhook delivery, and external HTTP call
    out of the service. Mirrors the field set callers see in the
    transaction-audit dashboard.
    """
    payload = {
        "event": "outbound_call",
        "kind": kind,
        "target": target,
        "duration_ms": duration_ms,
        "status": status,
        **extra,
    }
    if cost_usd is not None:
        payload["cost_usd"] = round(cost_usd, 6)
    logger.info("outbound_call", extra=payload)
