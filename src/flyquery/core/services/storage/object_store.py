# Copyright 2026 Firefly Software Solutions Inc
"""ObjectStore port (spec §9.1)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class ObjectMeta:
    key: str
    size_bytes: int
    content_type: str
    etag: str | None
    last_modified: datetime
    kms_key_uri: str | None = None


class ObjectStore(Protocol):
    """Hexagonal port: blob put/get/head/delete/list/presign/copy.

    Adapters: LocalFs (default), S3, GCS, AzureBlob. See spec §9.5
    for the key layout. KMS key handling is per-call so a workspace
    with workspace.kms_key_uri can upgrade above the storage-native
    default.
    """

    async def put(
        self,
        key: str,
        body: bytes | AsyncIterator[bytes],
        content_type: str,
        kms_key_uri: str | None = None,
    ) -> ObjectMeta: ...

    async def get(self, key: str) -> AsyncIterator[bytes]: ...
    async def head(self, key: str) -> ObjectMeta: ...
    async def delete(self, key: str) -> None: ...
    async def list(self, prefix: str) -> AsyncIterator[ObjectMeta]: ...
    async def presign_get(self, key: str, ttl_s: int) -> str: ...
    async def copy(self, src_key: str, dst_key: str) -> None: ...
