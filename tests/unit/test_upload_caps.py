import pytest
from flyquery.core.services.ingestion.caps import (
    enforce_upload_cap,
    FileTooLargeError,
    WorkspaceQuotaExceededError,
)


class _FakeSettings:
    """Minimal settings stand-in for caps tests."""

    def __init__(self, max_file_mb: int = 100, max_workspace_gb: int = 10):
        self.max_file_mb = max_file_mb
        self.max_workspace_gb = max_workspace_gb


def test_file_within_limits():
    settings = _FakeSettings(max_file_mb=100, max_workspace_gb=10)
    # 50 MB file, 1 GB used → no error
    enforce_upload_cap(
        size_bytes=50 * 1024 * 1024,
        workspace_storage_used_bytes=1 * 1024 * 1024 * 1024,
        settings=settings,
    )


def test_file_too_large_raises_413():
    settings = _FakeSettings(max_file_mb=100, max_workspace_gb=10)
    with pytest.raises(FileTooLargeError) as exc_info:
        enforce_upload_cap(
            size_bytes=101 * 1024 * 1024,  # 101 MB > 100 MB limit
            workspace_storage_used_bytes=0,
            settings=settings,
        )
    assert exc_info.value.http_status == 413


def test_workspace_quota_exceeded_raises_507():
    settings = _FakeSettings(max_file_mb=100, max_workspace_gb=10)
    with pytest.raises(WorkspaceQuotaExceededError) as exc_info:
        enforce_upload_cap(
            size_bytes=50 * 1024 * 1024,  # 50 MB file
            workspace_storage_used_bytes=9 * 1024 * 1024 * 1024 + 990 * 1024 * 1024,  # 9990 MB used → total > 10 GB
            settings=settings,
        )
    assert exc_info.value.http_status == 507


def test_exact_file_limit_is_allowed():
    settings = _FakeSettings(max_file_mb=100, max_workspace_gb=10)
    # Exactly 100 MB = allowed (boundary condition: <= not <)
    enforce_upload_cap(
        size_bytes=100 * 1024 * 1024,
        workspace_storage_used_bytes=0,
        settings=settings,
    )


def test_zero_size_file_is_always_allowed():
    settings = _FakeSettings(max_file_mb=100, max_workspace_gb=10)
    enforce_upload_cap(
        size_bytes=0,
        workspace_storage_used_bytes=0,
        settings=settings,
    )
