# Copyright 2026 Firefly Software Solutions Inc
"""AzureBlob ObjectStore adapter (azure-storage-blob async)."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

from flyquery.core.services.storage.object_store import ObjectMeta

# Standard Azurite connection string used in local dev / tests.
_AZURITE_CONN = (
    "DefaultEndpointsProtocol=http;"
    "AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tiqIFBg==;"
    "BlobEndpoint=http://{host}:{port}/devstoreaccount1;"
)


class AzureBlobObjectStore:
    """Bucket-relative ObjectStore backed by Azure Blob Storage.

    `base` is `azure://<container>[/<prefix>]`.

    Authentication priority:
    1. Explicit `connection_string` argument.
    2. ``AZURE_STORAGE_CONNECTION_STRING`` environment variable.

    Customer-managed encryption uses `encryption_scope` if provided.
    """

    def __init__(
        self,
        base: str,
        connection_string: str | None = None,
        encryption_scope: str | None = None,
        presign_ttl_s: int = 86400,
    ) -> None:
        u = urlparse(base)
        if u.scheme != "azure":
            raise ValueError(f"AzureBlob base must be azure://...; got {base!r}")
        self._container = u.netloc
        self._prefix = u.path.lstrip("/")
        self._conn_str: str = (
            connection_string
            or os.environ.get("AZURE_STORAGE_CONNECTION_STRING", "")
        )
        self._encryption_scope = encryption_scope
        self._presign_ttl_s = presign_ttl_s

    # ------------------------------------------------------------------
    # Key helpers
    # ------------------------------------------------------------------

    def _full_key(self, key: str) -> str:
        if ".." in key.split("/"):
            raise ValueError(f"illegal key {key!r}")
        return f"{self._prefix}/{key}".lstrip("/")

    def _strip_prefix(self, full_key: str) -> str:
        if self._prefix and full_key.startswith(self._prefix + "/"):
            return full_key[len(self._prefix) + 1:]
        return full_key

    # ------------------------------------------------------------------
    # Service client
    # ------------------------------------------------------------------

    def _service_client(self):
        from azure.storage.blob.aio import BlobServiceClient  # type: ignore[import-untyped]

        if not self._conn_str:
            raise RuntimeError(
                "AzureBlobObjectStore: no connection string. "
                "Set AZURE_STORAGE_CONNECTION_STRING or pass connection_string=."
            )
        return BlobServiceClient.from_connection_string(self._conn_str)

    async def _ensure_container(self, service_client: Any) -> None:
        """Create the container if it does not exist yet."""
        try:
            container_client = service_client.get_container_client(self._container)
            await container_client.create_container()
        except Exception as exc:
            msg = str(exc).lower()
            if "already exists" in msg or "containeralreadyexists" in msg:
                return
            raise

    # ------------------------------------------------------------------
    # ObjectStore protocol
    # ------------------------------------------------------------------

    async def put(
        self,
        key: str,
        body: bytes | AsyncIterator[bytes],
        content_type: str,
        kms_key_uri: str | None = None,
    ) -> ObjectMeta:
        full = self._full_key(key)

        if isinstance(body, (bytes, bytearray, memoryview)):
            data: bytes = bytes(body)
        else:
            chunks: list[bytes] = []
            async for chunk in body:
                chunks.append(chunk)
            data = b"".join(chunks)

        size = len(data)
        upload_kwargs: dict[str, Any] = {
            "data": data,
            "overwrite": True,
            "content_settings": _content_settings(content_type),
        }
        if self._encryption_scope:
            upload_kwargs["encryption_scope"] = self._encryption_scope
        if kms_key_uri:
            # Azure customer-managed key is configured at the account level;
            # pass the scope name via encryption_scope when available.
            upload_kwargs.setdefault("encryption_scope", kms_key_uri)

        async with self._service_client() as svc:
            await self._ensure_container(svc)
            blob_client = svc.get_blob_client(container=self._container, blob=full)
            await blob_client.upload_blob(**upload_kwargs)

        return ObjectMeta(
            key=key,
            size_bytes=size,
            content_type=content_type,
            etag=None,
            last_modified=datetime.now(tz=timezone.utc),
            kms_key_uri=kms_key_uri,
        )

    async def get(self, key: str) -> AsyncIterator[bytes]:
        full = self._full_key(key)

        async def _stream() -> AsyncIterator[bytes]:
            async with self._service_client() as svc:
                blob_client = svc.get_blob_client(container=self._container, blob=full)
                stream = await blob_client.download_blob()
                data = await stream.readall()
                yield data

        return _stream()

    async def head(self, key: str) -> ObjectMeta:
        from azure.core.exceptions import ResourceNotFoundError  # type: ignore[import-untyped]

        full = self._full_key(key)
        async with self._service_client() as svc:
            blob_client = svc.get_blob_client(container=self._container, blob=full)
            try:
                props = await blob_client.get_blob_properties()
            except ResourceNotFoundError as exc:
                raise FileNotFoundError(key) from exc
            size = props.get("size", 0) or 0
            ct = props.get("content_settings", {}).get("content_type", "application/octet-stream") or "application/octet-stream"
            etag = props.get("etag")
            lm = props.get("last_modified") or datetime.now(tz=timezone.utc)
            return ObjectMeta(
                key=key,
                size_bytes=int(size),
                content_type=ct,
                etag=str(etag).strip('"') if etag else None,
                last_modified=lm,
            )

    async def delete(self, key: str) -> None:
        full = self._full_key(key)
        async with self._service_client() as svc:
            blob_client = svc.get_blob_client(container=self._container, blob=full)
            await blob_client.delete_blob()

    async def list(self, prefix: str) -> AsyncIterator[ObjectMeta]:
        full_prefix = self._full_key(prefix)

        async def _gen() -> AsyncIterator[ObjectMeta]:
            async with self._service_client() as svc:
                container_client = svc.get_container_client(self._container)
                async for blob in container_client.list_blobs(name_starts_with=full_prefix):
                    name = blob["name"]
                    size = blob.get("size", 0) or 0
                    ct = (blob.get("content_settings") or {}).get("content_type", "application/octet-stream") or "application/octet-stream"
                    etag = blob.get("etag")
                    lm = blob.get("last_modified") or datetime.now(tz=timezone.utc)
                    yield ObjectMeta(
                        key=self._strip_prefix(name),
                        size_bytes=int(size),
                        content_type=ct,
                        etag=str(etag).strip('"') if etag else None,
                        last_modified=lm,
                    )

        return _gen()

    async def presign_get(self, key: str, ttl_s: int) -> str:
        """Return a SAS URL for GET access.

        Against Azurite the account key is well-known so SAS generation
        works offline without real Azure credentials.
        """
        from datetime import timedelta
        from azure.storage.blob import (  # type: ignore[import-untyped]
            BlobSasPermissions,
            generate_blob_sas,
        )

        full = self._full_key(key)

        # Parse account name + account key from connection string
        account_name, account_key = _parse_conn_str_creds(self._conn_str)

        sas = generate_blob_sas(
            account_name=account_name,
            container_name=self._container,
            blob_name=full,
            account_key=account_key,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.now(tz=timezone.utc) + timedelta(seconds=ttl_s),
        )
        # Build the full URL; use endpoint from connection string if present.
        endpoint = _parse_blob_endpoint(self._conn_str, account_name)
        return f"{endpoint}/{self._container}/{full}?{sas}"

    async def copy(self, src_key: str, dst_key: str) -> None:
        src_full = self._full_key(src_key)
        dst_full = self._full_key(dst_key)

        async with self._service_client() as svc:
            src_client = svc.get_blob_client(container=self._container, blob=src_full)
            dst_client = svc.get_blob_client(container=self._container, blob=dst_full)
            src_url = src_client.url
            await dst_client.start_copy_from_url(src_url)


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def _content_settings(content_type: str) -> Any:
    """Return a ContentSettings object for upload."""
    from azure.storage.blob import ContentSettings  # type: ignore[import-untyped]
    return ContentSettings(content_type=content_type)


def _parse_conn_str_creds(conn_str: str) -> tuple[str, str]:
    """Extract AccountName and AccountKey from a connection string."""
    parts = {p.split("=", 1)[0]: p.split("=", 1)[1] for p in conn_str.split(";") if "=" in p}
    return parts.get("AccountName", ""), parts.get("AccountKey", "")


def _parse_blob_endpoint(conn_str: str, account_name: str) -> str:
    """Extract BlobEndpoint from connection string, or build a default."""
    parts = {p.split("=", 1)[0]: p.split("=", 1)[1] for p in conn_str.split(";") if "=" in p}
    if "BlobEndpoint" in parts:
        return parts["BlobEndpoint"].rstrip("/")
    protocol = parts.get("DefaultEndpointsProtocol", "https")
    suffix = parts.get("EndpointSuffix", "core.windows.net")
    return f"{protocol}://{account_name}.blob.{suffix}"
