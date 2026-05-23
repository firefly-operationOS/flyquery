# Copyright 2026 Firefly Software Solutions Inc
"""All entity modules import + the Base.metadata enumerates the tables."""

from __future__ import annotations


def test_lifecycle_entities_register_on_base_metadata() -> None:
    from flyquery.models.entities import Base
    table_names = set(Base.metadata.tables.keys())
    assert {"flyquery_workspaces", "flyquery_datasets", "flyquery_files", "flyquery_tables"} <= table_names
