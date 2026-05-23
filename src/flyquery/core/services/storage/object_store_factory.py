# Copyright 2026 Firefly Software Solutions Inc
"""Factory: choose ObjectStore adapter from FlyquerySettings."""

from __future__ import annotations

from flyquery.config import FlyquerySettings
from flyquery.core.services.storage.object_store import ObjectStore

try:
    from flyquery.core.services.storage.adapters.s3 import S3ObjectStore  # noqa: F401
    _HAS_S3 = True
except ImportError:
    _HAS_S3 = False


def build_object_store(settings: FlyquerySettings) -> ObjectStore:
    kind = settings.object_store
    if kind == "local":
        from flyquery.core.services.storage.adapters.local_fs import LocalFsObjectStore
        return LocalFsObjectStore(base=settings.object_store_base, presign_ttl_s=settings.object_store_presign_ttl_s)
    if kind == "s3":
        if not _HAS_S3:
            raise RuntimeError(
                "object_store=s3 selected but the 's3' extra is not installed; "
                "run: uv sync --extra s3"
            )
        from flyquery.core.services.storage.adapters.s3 import S3ObjectStore
        return S3ObjectStore(base=settings.object_store_base, presign_ttl_s=settings.object_store_presign_ttl_s)
    if kind == "gcs":
        raise NotImplementedError("GCS adapter ships in Plan 2 task 15")
    if kind == "azure":
        raise NotImplementedError("AzureBlob adapter ships in Plan 2 task 15")
    raise ValueError(f"unknown object_store kind: {kind!r}")
