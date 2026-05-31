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
