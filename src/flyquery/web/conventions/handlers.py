# Copyright 2026 Firefly Software Solutions Inc
"""Register exception → ProblemDetail handlers on a FastAPI app.

We hand-register handlers via :meth:`fastapi.FastAPI.add_exception_handler`
because pyfly's ``@controller_advice`` scanner does not pick up
beans in FastAPI mode. One day pyfly will fix the scanner; until
then this module is authoritative.

In addition to the in-house :class:`FireflyHTTPException` hierarchy we
bridge the pyfly kernel + CQRS exception classes raised across
flyquery/flyradar handler code (``ResourceNotFoundException``,
``InvalidRequestException``, ``CommandProcessingException``).
Without these bridges the global pyfly handler catches them first
and renders the legacy ``{error: {...}}`` envelope with
``application/json`` -- callers would see two envelopes depending
on which exception fired.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pyfly.cqrs.exceptions import CommandProcessingException
from pyfly.kernel import (
    InvalidRequestException,
    ResourceNotFoundException,
)

from flyquery.web.conventions.context import current_tenant_context
from flyquery.web.conventions.errors import ProblemDetail
from flyquery.web.conventions.exceptions import (
    CommandProcessingError,
    FireflyHTTPException,
    InvalidRequest,
    ResourceNotFound,
)

_MEDIA_TYPE = "application/problem+json"
_LOC_SOURCES = {"body", "query", "path", "header", "cookie"}


def _to_problem(exc: FireflyHTTPException, request: Request) -> ProblemDetail:
    ctx = current_tenant_context()
    return ProblemDetail(
        type=exc.type_uri,
        code=exc.code,
        title=exc.title,
        status=exc.status,
        detail=exc.detail,
        instance=exc.instance or str(request.url.path),
        correlation_id=ctx.correlation_id if ctx else None,
        errors=exc.errors,
    )


def _problem_response(problem: ProblemDetail) -> JSONResponse:
    return JSONResponse(
        status_code=problem.status,
        content=problem.model_dump(mode="json"),
        media_type=_MEDIA_TYPE,
    )


def _trim_loc(loc: tuple[Any, ...] | list[Any]) -> tuple[Any, ...]:
    if loc and loc[0] in _LOC_SOURCES:
        return tuple(loc[1:])
    return tuple(loc)


async def _on_firefly(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, FireflyHTTPException)
    return _problem_response(_to_problem(exc, request))


async def _on_pydantic_validation(request: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)
    errors = [
        {
            "code": err.get("type", "invalid"),
            "path": ".".join(str(p) for p in _trim_loc(err.get("loc", ()))),
            "message": err.get("msg", ""),
        }
        for err in exc.errors()
    ]
    wrapped = InvalidRequest("Request validation failed.", errors=errors)
    return _problem_response(_to_problem(wrapped, request))


async def _on_pyfly_resource_not_found(request: Request, exc: Exception) -> JSONResponse:
    """Bridge pyfly's ``ResourceNotFoundException`` to ``ResourceNotFound``.

    Used by handlers + the SSE endpoint when an entity isn't found.
    Without this bridge pyfly's global handler renders the legacy
    ``{error: {...}}`` envelope.
    """
    assert isinstance(exc, ResourceNotFoundException)
    wrapped = ResourceNotFound(str(exc) or "Resource not found.")
    return _problem_response(_to_problem(wrapped, request))


async def _on_pyfly_invalid_request(request: Request, exc: Exception) -> JSONResponse:
    """Bridge pyfly's ``InvalidRequestException`` to ``InvalidRequest``.

    Used by ``billing_controller`` / ``dependencies_controller`` /
    ``jobs_controller`` for query-parameter validation failures, and by
    ``diff_service`` for malformed diff inputs.
    """
    assert isinstance(exc, InvalidRequestException)
    wrapped = InvalidRequest(str(exc) or "Invalid request.")
    return _problem_response(_to_problem(wrapped, request))


async def _on_pyfly_command_processing(request: Request, exc: Exception) -> JSONResponse:
    """Unwrap ``CommandProcessingException`` and render its cause.

    Pyfly's :class:`pyfly.cqrs.DefaultCommandBus` wraps every handler
    error in :class:`CommandProcessingException`. We unwrap the cause
    and dispatch on its concrete type:

    * ``FireflyHTTPException`` -- render directly (preserves status,
      code, title).
    * pyfly ``ResourceNotFoundException`` -- map to ``ResourceNotFound``.
    * pyfly ``InvalidRequestException`` -- map to ``InvalidRequest``.
    * Anything else (raw ``ValueError`` etc.) -- fall back to a 500
      :class:`CommandProcessingError` so the caller still sees a
      ``ProblemDetail`` envelope instead of pyfly's legacy shape.
    """
    assert isinstance(exc, CommandProcessingException)
    cause = getattr(exc, "cause", None) or exc.__cause__
    if isinstance(cause, FireflyHTTPException):
        return _problem_response(_to_problem(cause, request))
    if isinstance(cause, ResourceNotFoundException):
        wrapped = ResourceNotFound(str(cause))
        return _problem_response(_to_problem(wrapped, request))
    if isinstance(cause, InvalidRequestException):
        wrapped: FireflyHTTPException = InvalidRequest(str(cause))
        return _problem_response(_to_problem(wrapped, request))
    fallback = CommandProcessingError(str(exc) or "Command processing failed.")
    return _problem_response(_to_problem(fallback, request))


def register_exception_handlers(app: FastAPI) -> None:
    """Wire conventions + pyfly exception handlers on ``app``.

    Registers:

    * :class:`FireflyHTTPException` → ``ProblemDetail`` envelope.
    * :class:`RequestValidationError` → ``invalid_request`` with the
      per-field ``errors`` list populated.
    * pyfly ``ResourceNotFoundException`` / ``InvalidRequestException``
      → ``ProblemDetail`` envelope so the legacy global handler doesn't
      win.
    * pyfly ``CommandProcessingException`` → unwrap the cause and
      render via the rules above (falls back to 500
      ``command_processing_error`` for unrecognised causes).
    """
    app.add_exception_handler(FireflyHTTPException, _on_firefly)
    app.add_exception_handler(RequestValidationError, _on_pydantic_validation)
    app.add_exception_handler(ResourceNotFoundException, _on_pyfly_resource_not_found)
    app.add_exception_handler(InvalidRequestException, _on_pyfly_invalid_request)
    app.add_exception_handler(CommandProcessingException, _on_pyfly_command_processing)
