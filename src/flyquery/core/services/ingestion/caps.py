# Copyright 2026 Firefly Software Solutions Inc
"""Upload cap enforcement (per-file + per-workspace quota)."""

from __future__ import annotations

from typing import Any, Protocol


class _CapsSettings(Protocol):
    """Minimal settings shape expected by `enforce_upload_cap`."""

    max_file_mb: int
    max_workspace_gb: int


class FileTooLargeError(Exception):
    """File exceeds the per-upload size limit (HTTP 413)."""

    http_status: int = 413

    def __init__(self, size_bytes: int, limit_bytes: int) -> None:
        super().__init__(
            f"File size {size_bytes:,} bytes exceeds the {limit_bytes:,}-byte "
            f"({limit_bytes // (1024 ** 2)} MB) per-file upload limit."
        )
        self.size_bytes = size_bytes
        self.limit_bytes = limit_bytes


class WorkspaceQuotaExceededError(Exception):
    """Adding this file would exceed the workspace storage quota (HTTP 507)."""

    http_status: int = 507

    def __init__(self, current_bytes: int, addition_bytes: int, quota_bytes: int) -> None:
        super().__init__(
            f"Workspace would reach {(current_bytes + addition_bytes):,} bytes "
            f"which exceeds the {quota_bytes:,}-byte "
            f"({quota_bytes // (1024 ** 3)} GB) workspace quota."
        )
        self.current_bytes = current_bytes
        self.addition_bytes = addition_bytes
        self.quota_bytes = quota_bytes


def enforce_upload_cap(
    size_bytes: int,
    workspace_storage_used_bytes: int | float,
    settings: _CapsSettings,
) -> None:
    """Raise FileTooLargeError (413) or WorkspaceQuotaExceededError (507) when limits are hit.

    Args:
        size_bytes: Size of the incoming upload in bytes.
        workspace_storage_used_bytes: Current total bytes stored in the workspace.
        settings: Object with `max_file_mb` and `max_workspace_gb` attributes.
    """
    max_file_bytes = settings.max_file_mb * 1024 * 1024
    max_workspace_bytes = settings.max_workspace_gb * 1024 * 1024 * 1024

    if size_bytes > max_file_bytes:
        raise FileTooLargeError(size_bytes, max_file_bytes)

    if int(workspace_storage_used_bytes) + size_bytes > max_workspace_bytes:
        raise WorkspaceQuotaExceededError(
            int(workspace_storage_used_bytes), size_bytes, max_workspace_bytes
        )
