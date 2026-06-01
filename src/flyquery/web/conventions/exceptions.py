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

"""Concrete exception classes that map 1:1 to ProblemDetail rows.

Each subclass declares its ``status``, ``code``, ``title`` as
class attributes. The handler renders any ``FireflyHTTPException``
to a ``ProblemDetail`` JSON response without per-class mapper code.

Adding a new error type = adding a new subclass here + (optionally)
documenting it in the OpenAPI spec.
"""

from __future__ import annotations

from typing import Any, ClassVar

_BASE_URI = "https://firefly.dev/problems"


class FireflyHTTPException(Exception):
    """Base class. Concrete subclasses set ``status``, ``code``, ``title``."""

    status: ClassVar[int] = 0
    code: ClassVar[str] = ""
    title: ClassVar[str] = ""

    def __init__(
        self,
        detail: str,
        *,
        errors: list[dict[str, Any]] | None = None,
        instance: str | None = None,
    ) -> None:
        # Subclasses must override these three class attrs. The
        # base raises so a typo (e.g. missing ``code``) surfaces at
        # construction time instead of at the JSON-render step.
        assert self.status > 0, f"{type(self).__name__}.status must be set"
        assert self.code, f"{type(self).__name__}.code must be set"
        assert self.title, f"{type(self).__name__}.title must be set"
        super().__init__(detail)
        self.detail = detail
        self.errors = errors or []
        self.instance = instance

    @property
    def type_uri(self) -> str:
        return f"{_BASE_URI}/{self.code}"


# -- 400 -------------------------------------------------------------


class MissingIdempotencyKey(FireflyHTTPException):
    status = 400
    code = "missing_idempotency_key"
    title = "Missing Idempotency-Key header"


class MissingTenantContext(FireflyHTTPException):
    status = 400
    code = "missing_tenant_context"
    title = "Missing tenant context"


class InvalidRequest(FireflyHTTPException):
    status = 422
    code = "invalid_request"
    title = "Invalid request"


# -- 402 -------------------------------------------------------------


class BudgetExceeded(FireflyHTTPException):
    status = 402
    code = "budget_exceeded"
    title = "Budget exceeded"


# -- 403 -------------------------------------------------------------


class TenantClaimMismatch(FireflyHTTPException):
    status = 403
    code = "tenant_claim_mismatch"
    title = "Tenant claim mismatch"


# -- 404 -------------------------------------------------------------


class ResourceNotFound(FireflyHTTPException):
    status = 404
    code = "resource_not_found"
    title = "Resource not found"


class WorkspaceNotFound(FireflyHTTPException):
    status = 404
    code = "workspace_not_found"
    title = "Workspace not found"


# -- 409 -------------------------------------------------------------


class IdempotencyKeyConflict(FireflyHTTPException):
    status = 409
    code = "idempotency_key_conflict"
    title = "Idempotency-Key conflict"


# -- 500 -------------------------------------------------------------


class CommandProcessingError(FireflyHTTPException):
    """Fallback for pyfly ``CommandProcessingException`` causes we don't
    know how to map.

    The conventions handler unwraps the wrapped ``cause`` and renders
    its concrete type (``FireflyHTTPException`` or
    ``ResourceNotFoundException``) directly when possible. When the
    cause is something we don't recognise (e.g. a raw ``ValueError``)
    we fall back to this 500 so the caller still gets the
    ``ProblemDetail`` envelope instead of pyfly's legacy ``{error: ...}``
    shape.
    """

    status = 500
    code = "command_processing_error"
    title = "Command processing error"
