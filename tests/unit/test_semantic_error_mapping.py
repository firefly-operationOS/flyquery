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

"""SemanticCompileError must surface as an RFC 7807 400, not a 500."""

from __future__ import annotations

from fastapi import FastAPI
from starlette.testclient import TestClient

from flyquery.core.services.semantic.errors import MetricYamlError, SemanticCompileError
from flyquery.web.semantic_error_handler import register_semantic_error_handler


def _app() -> FastAPI:
    app = FastAPI()

    @app.get("/boom-metric")
    def _boom_metric() -> None:
        raise MetricYamlError("bad agg", field="type_params.measure.agg")

    @app.get("/boom-base")
    def _boom_base() -> None:
        raise SemanticCompileError("function not allowed: READ_CSV_AUTO", field="filter")

    register_semantic_error_handler(app)
    return app


def test_metric_yaml_error_maps_to_400() -> None:
    client = TestClient(_app(), raise_server_exceptions=False)
    resp = client.get("/boom-metric")
    assert resp.status_code == 400
    body = resp.json()
    assert body["code"] == "semantic_compile_error"
    assert body["status"] == 400
    assert body["errors"][0]["path"] == "type_params.measure.agg"


def test_base_compile_error_maps_to_400() -> None:
    client = TestClient(_app(), raise_server_exceptions=False)
    resp = client.get("/boom-base")
    assert resp.status_code == 400
    assert resp.json()["code"] == "semantic_compile_error"
    assert resp.headers["content-type"].startswith("application/problem+json")
