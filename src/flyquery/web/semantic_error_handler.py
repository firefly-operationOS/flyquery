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

"""flyquery-local handler mapping ``SemanticCompileError`` to RFC 7807 400.

The semantic layer is flyquery-specific, so this handler lives outside the
lock-stepped ``web/conventions`` package (which must stay byte-identical
across canon/radar/flyquery). It is registered from ``flyquery.main`` right
after the shared conventions handler table.
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.requests import Request

from flyquery.core.services.semantic.errors import SemanticCompileError
from flyquery.web.conventions.errors import ProblemDetail

_MEDIA_TYPE = "application/problem+json"
_TYPE_URI = "https://firefly.dev/problems/semantic_compile_error"


async def _on_semantic_compile(request: Request, exc: Exception) -> JSONResponse:
    """Render a :class:`SemanticCompileError` as the canonical 400 envelope."""
    assert isinstance(exc, SemanticCompileError)
    errors = (
        [{"code": exc.code, "path": exc.field, "message": exc.detail}] if exc.field else []
    )
    problem = ProblemDetail(
        type=_TYPE_URI,
        code="semantic_compile_error",
        title="Semantic compile error",
        status=400,
        detail=exc.detail,
        instance=str(request.url.path),
        errors=errors,
    )
    return JSONResponse(
        status_code=400,
        content=problem.model_dump(mode="json"),
        media_type=_MEDIA_TYPE,
    )


def register_semantic_error_handler(app: FastAPI) -> None:
    """Register the semantic-compile-error → 400 handler on ``app``."""
    app.add_exception_handler(SemanticCompileError, _on_semantic_compile)
