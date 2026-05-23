# Copyright 2026 Firefly Software Solutions Inc
# tests/unit/test_workspace_service.py
import pytest

from flyquery.core.services.workspaces.workspace_service import WorkspaceService
from flyquery.interfaces.workspaces import WorkspaceCreate


class FakeRepo:
    def __init__(self):
        self.rows = []

    async def create(self, **fields):
        self.rows.append(fields)
        return {**fields, "id": "ws-1"}

    async def list_by_tenant(self, tenant_id):
        return [r for r in self.rows if r["tenant_id"] == tenant_id]


@pytest.mark.asyncio
async def test_create_workspace_assigns_defaults() -> None:
    svc = WorkspaceService(FakeRepo())
    ws = await svc.create("tenant-a", WorkspaceCreate(slug="alpha", name="Alpha"))
    assert ws["allow_direct_sql"] is False
    assert ws["default_locale"] == "en-US"
    assert ws["status"] == "ACTIVE"
