# Copyright 2026 Firefly Software Solutions Inc
"""Local-filesystem ObjectStore adapter (spec §9.1)."""

from __future__ import annotations

import shutil
from collections.abc import AsyncIterator
from datetime import datetime
from pathlib import Path

import aiofiles
import aiofiles.os

from flyquery.core.services.storage.object_store import ObjectMeta


class LocalFsObjectStore:
    """ObjectStore implementation against a local POSIX filesystem.

    `base` is the bucket root; keys are joined with it. Presigned URLs
    are emitted as `file://<absolute-path>` for dev visibility (no
    auth surface; for tests + local-only deploys only).
    """

    def __init__(self, base: str, presign_ttl_s: int = 86400) -> None:
        self._base = Path(base).expanduser().resolve()
        self._base.mkdir(parents=True, exist_ok=True)
        self._presign_ttl_s = presign_ttl_s

    def _abs(self, key: str) -> Path:
        # Reject path traversal
        if ".." in key.split("/"):
            raise ValueError(f"illegal key {key!r}")
        return self._base / key

    async def put(
        self,
        key: str,
        body,  # bytes | AsyncIterator[bytes]
        content_type: str,
        kms_key_uri: str | None = None,
    ) -> ObjectMeta:
        p = self._abs(key)
        p.parent.mkdir(parents=True, exist_ok=True)
        size = 0
        async with aiofiles.open(p, "wb") as f:
            if isinstance(body, (bytes, bytearray, memoryview)):
                await f.write(bytes(body))
                size = len(body)
            else:
                async for chunk in body:
                    await f.write(chunk)
                    size += len(chunk)
        return ObjectMeta(
            key=key,
            size_bytes=size,
            content_type=content_type,
            etag=None,
            last_modified=datetime.utcnow(),
            kms_key_uri=kms_key_uri,
        )

    async def get(self, key: str) -> AsyncIterator[bytes]:
        p = self._abs(key)
        if not p.exists():
            raise FileNotFoundError(key)

        async def _stream() -> AsyncIterator[bytes]:
            async with aiofiles.open(p, "rb") as f:
                while True:
                    chunk = await f.read(64 * 1024)
                    if not chunk:
                        break
                    yield chunk
        return _stream()

    async def head(self, key: str) -> ObjectMeta:
        p = self._abs(key)
        if not p.exists():
            raise FileNotFoundError(key)
        stat = await aiofiles.os.stat(p)
        return ObjectMeta(
            key=key,
            size_bytes=stat.st_size,
            content_type="application/octet-stream",
            etag=None,
            last_modified=datetime.utcfromtimestamp(stat.st_mtime),
        )

    async def delete(self, key: str) -> None:
        p = self._abs(key)
        if p.exists():
            await aiofiles.os.remove(p)

    async def list(self, prefix: str) -> AsyncIterator[ObjectMeta]:
        async def _gen() -> AsyncIterator[ObjectMeta]:
            root = self._abs(prefix) if prefix else self._base
            for path in root.rglob("*"):
                if path.is_file():
                    rel = path.relative_to(self._base).as_posix()
                    stat = path.stat()
                    yield ObjectMeta(
                        key=rel,
                        size_bytes=stat.st_size,
                        content_type="application/octet-stream",
                        etag=None,
                        last_modified=datetime.utcfromtimestamp(stat.st_mtime),
                    )
        return _gen()

    async def presign_get(self, key: str, ttl_s: int) -> str:
        return f"file://{self._abs(key).as_posix()}"

    async def copy(self, src_key: str, dst_key: str) -> None:
        src, dst = self._abs(src_key), self._abs(dst_key)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
