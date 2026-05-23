# Copyright 2026 Firefly Software Solutions Inc
"""ObjectStore port + factory re-exports."""

from flyquery.core.services.storage.object_store import ObjectMeta, ObjectStore
from flyquery.core.services.storage.object_store_factory import build_object_store

__all__ = ["ObjectStore", "ObjectMeta", "build_object_store"]
