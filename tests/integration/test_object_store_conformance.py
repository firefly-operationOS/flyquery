# Copyright 2026 Firefly Software Solutions Inc
# tests/integration/test_object_store_conformance.py
import uuid
from pathlib import Path

import pytest


def _local_factory(tmp: Path):
    from flyquery.core.services.storage.adapters.local_fs import LocalFsObjectStore
    return LocalFsObjectStore(base=str(tmp), presign_ttl_s=60)


@pytest.fixture(params=["local", "s3"])
def store(request, tmp_path, minio_container):
    if request.param == "local":
        return _local_factory(tmp_path)
    if request.param == "s3":
        from flyquery.core.services.storage.adapters.s3 import S3ObjectStore
        cfg = minio_container.get_config()
        return S3ObjectStore(
            base="s3://flyquery-test",
            endpoint_url=f"http://{cfg['endpoint']}",
            access_key=minio_container.access_key,
            secret_key=minio_container.secret_key,
            presign_ttl_s=60,
        )
    pytest.skip(f"no fixture for {request.param}")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_put_then_head_then_get(store) -> None:
    key = f"unit/{uuid.uuid4()}/blob.txt"
    body = b"hello flyquery"
    meta = await store.put(key, body, content_type="text/plain")
    assert meta.size_bytes == len(body)
    h = await store.head(key)
    assert h.size_bytes == len(body)
    parts: list[bytes] = []
    async for chunk in await store.get(key):
        parts.append(chunk)
    assert b"".join(parts) == body


@pytest.mark.integration
@pytest.mark.asyncio
async def test_delete_then_head_404(store) -> None:
    key = f"unit/{uuid.uuid4()}/x.bin"
    await store.put(key, b"data", content_type="application/octet-stream")
    await store.delete(key)
    with pytest.raises(FileNotFoundError):
        await store.head(key)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_list_prefix(store) -> None:
    prefix = f"unit/{uuid.uuid4()}/"
    for n in range(3):
        await store.put(f"{prefix}f{n}.bin", b"x", content_type="application/octet-stream")
    seen = []
    async for m in await store.list(prefix):
        seen.append(m.key)
    assert len(seen) == 3


@pytest.mark.integration
@pytest.mark.asyncio
async def test_presign_get(store) -> None:
    key = f"unit/{uuid.uuid4()}/p.bin"
    await store.put(key, b"presigned", content_type="application/octet-stream")
    url = await store.presign_get(key, ttl_s=60)
    assert isinstance(url, str) and len(url) > 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_copy(store) -> None:
    src = f"unit/{uuid.uuid4()}/src.bin"
    dst = f"unit/{uuid.uuid4()}/dst.bin"
    await store.put(src, b"copy-me", content_type="application/octet-stream")
    await store.copy(src, dst)
    h = await store.head(dst)
    assert h.size_bytes == 7
