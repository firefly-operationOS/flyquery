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

import pytest

from flyquery.config import FlyquerySettings
from flyquery.core.services.storage.object_store_factory import build_object_store


def test_factory_returns_local_fs_by_default() -> None:
    s = FlyquerySettings(object_store="local", object_store_base="/tmp/flyquery-x")
    store = build_object_store(s)
    assert store.__class__.__name__ == "LocalFsObjectStore"


def test_factory_raises_on_s3_without_extra(monkeypatch) -> None:
    s = FlyquerySettings(object_store="s3")
    monkeypatch.setattr("flyquery.core.services.storage.object_store_factory._HAS_S3", False)
    with pytest.raises(RuntimeError, match="extra"):
        build_object_store(s)


def test_factory_raises_on_gcs_without_extra(monkeypatch) -> None:
    s = FlyquerySettings(object_store="gcs", object_store_base="gs://bucket")
    monkeypatch.setattr("flyquery.core.services.storage.object_store_factory._HAS_GCS", False)
    with pytest.raises(RuntimeError, match="gcs"):
        build_object_store(s)


def test_factory_raises_on_azure_without_extra(monkeypatch) -> None:
    s = FlyquerySettings(object_store="azure", object_store_base="azure://container")
    monkeypatch.setattr("flyquery.core.services.storage.object_store_factory._HAS_AZURE", False)
    with pytest.raises(RuntimeError, match="azure"):
        build_object_store(s)
