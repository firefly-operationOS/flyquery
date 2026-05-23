# Copyright 2026 Firefly Software Solutions Inc
"""S3 ObjectStore adapter (aiobotocore)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

import aiobotocore.session
from botocore.config import Config

from flyquery.core.services.storage.object_store import ObjectMeta


class S3ObjectStore:
    """Bucket-relative ObjectStore; honours per-call KMS key via SSE-KMS.

    `base` is `s3://<bucket>[/<prefix>]`. `endpoint_url` allows pointing
    at MinIO / S3-compatible services.
    """

    def __init__(
        self,
        base: str,
        endpoint_url: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        region: str = "us-east-1",
        presign_ttl_s: int = 86400,
    ) -> None:
        u = urlparse(base)
        if u.scheme != "s3":
            raise ValueError(f"S3 base must be s3://...; got {base!r}")
        self._bucket = u.netloc
        self._prefix = u.path.lstrip("/")
        self._endpoint_url = endpoint_url
        self._access_key = access_key
        self._secret_key = secret_key
        self._region = region
        self._presign_ttl_s = presign_ttl_s
        self._session = aiobotocore.session.get_session()

    def _full_key(self, key: str) -> str:
        # Reject path traversal
        if ".." in key.split("/"):
            raise ValueError(f"illegal key {key!r}")
        return f"{self._prefix}/{key}".lstrip("/")

    async def _client(self):
        return self._session.create_client(
            "s3",
            endpoint_url=self._endpoint_url,
            aws_access_key_id=self._access_key,
            aws_secret_access_key=self._secret_key,
            region_name=self._region,
            config=Config(signature_version="s3v4"),
        )

    async def _ensure_bucket(self, client) -> None:
        try:
            await client.head_bucket(Bucket=self._bucket)
        except Exception:
            await client.create_bucket(Bucket=self._bucket)

    async def put(self, key, body, content_type, kms_key_uri=None) -> ObjectMeta:
        full = self._full_key(key)
        kwargs: dict[str, Any] = {
            "Bucket": self._bucket,
            "Key": full,
            "ContentType": content_type,
        }
        if kms_key_uri:
            kwargs["ServerSideEncryption"] = "aws:kms"
            kwargs["SSEKMSKeyId"] = kms_key_uri
        async with await self._client() as client:
            await self._ensure_bucket(client)
            if isinstance(body, (bytes, bytearray, memoryview)):
                kwargs["Body"] = bytes(body)
                size = len(body)
                await client.put_object(**kwargs)
            else:
                # Stream via multipart for large bodies
                init = await client.create_multipart_upload(**kwargs)
                upload_id = init["UploadId"]
                parts = []
                part_n = 1
                size = 0
                async for chunk in body:
                    p = await client.upload_part(
                        Bucket=self._bucket,
                        Key=full,
                        PartNumber=part_n,
                        UploadId=upload_id,
                        Body=chunk,
                    )
                    parts.append({"ETag": p["ETag"], "PartNumber": part_n})
                    part_n += 1
                    size += len(chunk)
                await client.complete_multipart_upload(
                    Bucket=self._bucket,
                    Key=full,
                    UploadId=upload_id,
                    MultipartUpload={"Parts": parts},
                )
        return ObjectMeta(
            key=key,
            size_bytes=size,
            content_type=content_type,
            etag=None,
            last_modified=datetime.utcnow(),
            kms_key_uri=kms_key_uri,
        )

    async def get(self, key) -> AsyncIterator[bytes]:
        full = self._full_key(key)

        async def _stream() -> AsyncIterator[bytes]:
            async with await self._client() as client:
                resp = await client.get_object(Bucket=self._bucket, Key=full)
                async for chunk in resp["Body"]:
                    yield chunk

        return _stream()

    async def head(self, key) -> ObjectMeta:
        full = self._full_key(key)
        async with await self._client() as client:
            try:
                resp = await client.head_object(Bucket=self._bucket, Key=full)
            except client.exceptions.NoSuchKey as exc:
                raise FileNotFoundError(key) from exc
            except Exception as exc:  # botocore raises ClientError 404
                if getattr(exc, "response", {}).get("Error", {}).get("Code") in ("404", "NoSuchKey"):
                    raise FileNotFoundError(key) from exc
                raise
            return ObjectMeta(
                key=key,
                size_bytes=int(resp["ContentLength"]),
                content_type=resp.get("ContentType", "application/octet-stream"),
                etag=resp.get("ETag"),
                last_modified=resp["LastModified"],
            )

    async def delete(self, key) -> None:
        full = self._full_key(key)
        async with await self._client() as client:
            await client.delete_object(Bucket=self._bucket, Key=full)

    async def list(self, prefix) -> AsyncIterator[ObjectMeta]:
        full_prefix = self._full_key(prefix)

        async def _gen() -> AsyncIterator[ObjectMeta]:
            async with await self._client() as client:
                paginator = client.get_paginator("list_objects_v2")
                async for page in paginator.paginate(Bucket=self._bucket, Prefix=full_prefix):
                    for item in page.get("Contents", []):
                        yield ObjectMeta(
                            key=item["Key"][len(self._prefix) :].lstrip("/") if self._prefix else item["Key"],
                            size_bytes=int(item["Size"]),
                            content_type="application/octet-stream",
                            etag=item.get("ETag"),
                            last_modified=item["LastModified"],
                        )

        return _gen()

    async def presign_get(self, key, ttl_s) -> str:
        full = self._full_key(key)
        async with await self._client() as client:
            return await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self._bucket, "Key": full},
                ExpiresIn=ttl_s,
            )

    async def copy(self, src_key, dst_key) -> None:
        src_full = self._full_key(src_key)
        dst_full = self._full_key(dst_key)
        async with await self._client() as client:
            await client.copy_object(
                Bucket=self._bucket,
                Key=dst_full,
                CopySource={"Bucket": self._bucket, "Key": src_full},
            )
