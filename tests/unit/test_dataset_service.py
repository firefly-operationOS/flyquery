# Copyright 2026 Firefly Software Solutions Inc
import uuid

import pytest

from flyquery.core.services.datasets.dataset_service import DatasetService
from flyquery.interfaces.datasets import DatasetCreate


class FakeRepo:
    def __init__(self) -> None:
        self.rows: list = []

    async def create(self, **f):  # type: ignore[override]
        self.rows.append(f)
        return {**f, "id": str(uuid.uuid4())}

    async def list(self, tenant_id: str, workspace_id: uuid.UUID):
        return [r for r in self.rows if r["tenant_id"] == tenant_id and r["workspace_id"] == workspace_id]


@pytest.mark.asyncio
async def test_create_dataset_defaults_drift_policy_AUTO() -> None:
    svc = DatasetService(FakeRepo())  # type: ignore[arg-type]
    ws = uuid.uuid4()
    ds = await svc.create("tenant-a", ws, DatasetCreate(name="Sales 2026"))
    assert ds["drift_policy"] == "AUTO"
    assert ds["status"] == "ACTIVE"
