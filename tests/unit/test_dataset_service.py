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

import uuid
from dataclasses import dataclass

import pytest

from flyquery.core.services.datasets.dataset_service import DatasetService
from flyquery.interfaces.datasets import DatasetCreate


class FakeRepo:
    def __init__(self) -> None:
        self.rows: list = []
        self.purging: list[uuid.UUID] = []

    async def create(self, **f):  # type: ignore[override]
        self.rows.append(f)
        return {**f, "id": str(uuid.uuid4())}

    async def list(self, tenant_id: str, workspace_id: uuid.UUID):
        return [r for r in self.rows if r["tenant_id"] == tenant_id and r["workspace_id"] == workspace_id]

    async def mark_purging(self, dataset_id: uuid.UUID) -> None:
        self.purging.append(dataset_id)


@dataclass
class _StoredObject:
    key: str


class FakeObjectStore:
    """Minimal ObjectStore impl that records deletes."""

    def __init__(self, seeded: list[str]) -> None:
        self._keys = list(seeded)
        self.deleted: list[str] = []

    async def list(self, prefix: str):
        async def _gen():
            for k in self._keys:
                if k.startswith(prefix):
                    yield _StoredObject(key=k)

        return _gen()

    async def delete(self, key: str) -> None:
        self.deleted.append(key)


@pytest.mark.asyncio
async def test_create_dataset_defaults_drift_policy_AUTO() -> None:
    svc = DatasetService(FakeRepo())  # type: ignore[arg-type]
    ws = uuid.uuid4()
    ds = await svc.create("tenant-a", ws, DatasetCreate(name="Sales 2026"))
    assert ds["drift_policy"] == "AUTO"
    assert ds["status"] == "ACTIVE"


@pytest.mark.asyncio
async def test_purge_marks_purging_and_reclaims_blobs_under_dataset_prefix() -> None:
    """purge() flips status PURGING and removes every key under the
    canonical dataset prefix -- but never touches keys outside it."""
    repo = FakeRepo()
    svc = DatasetService(repo)  # type: ignore[arg-type]

    tenant = "acme"
    ws = uuid.UUID("00000000-0000-0000-0000-000000000001")
    ds = uuid.UUID("00000000-0000-0000-0000-000000000002")
    other_ds = uuid.UUID("00000000-0000-0000-0000-000000000003")

    store = FakeObjectStore(
        seeded=[
            f"flyquery/{tenant}/{ws}/{ds}/files/abc.csv",
            f"flyquery/{tenant}/{ws}/{ds}/tables/t1/v1.parquet",
            f"flyquery/{tenant}/{ws}/{ds}/derived/d1/v1.parquet",
            f"flyquery/{tenant}/{ws}/{ds}/results/q1.parquet",
            # Adjacent dataset under the same workspace -- must NOT be touched.
            f"flyquery/{tenant}/{ws}/{other_ds}/tables/x/v1.parquet",
            # Adjacent tenant -- must NOT be touched.
            f"flyquery/other-tenant/{ws}/{ds}/tables/x/v1.parquet",
        ],
    )

    await svc.purge(ds, object_store=store, tenant_id=tenant, workspace_id=ws)

    assert repo.purging == [ds]
    assert sorted(store.deleted) == sorted(
        [
            f"flyquery/{tenant}/{ws}/{ds}/files/abc.csv",
            f"flyquery/{tenant}/{ws}/{ds}/tables/t1/v1.parquet",
            f"flyquery/{tenant}/{ws}/{ds}/derived/d1/v1.parquet",
            f"flyquery/{tenant}/{ws}/{ds}/results/q1.parquet",
        ]
    )


@pytest.mark.asyncio
async def test_purge_is_safe_on_dataset_with_zero_blobs() -> None:
    """An empty store is fine -- mark_purging still runs, no deletes happen."""
    repo = FakeRepo()
    svc = DatasetService(repo)  # type: ignore[arg-type]
    ds = uuid.UUID("00000000-0000-0000-0000-000000000099")
    store = FakeObjectStore(seeded=[])
    await svc.purge(ds, object_store=store, tenant_id="acme", workspace_id=uuid.uuid4())
    assert repo.purging == [ds]
    assert store.deleted == []
