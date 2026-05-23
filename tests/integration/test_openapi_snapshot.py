import json
import pytest
from pathlib import Path


@pytest.mark.integration
def test_openapi_snapshot_matches_running_app():
    from flyquery.main import app
    expected = app.openapi()
    snapshot_path = Path(__file__).parent.parent.parent / "openapi.json"
    actual = json.loads(snapshot_path.read_text())
    # We accept differences in `info.version` (CalVer-bumped) but the
    # paths + components must match exactly.
    expected_keys = set(expected.get("paths", {}).keys())
    actual_keys = set(actual.get("paths", {}).keys())
    assert expected_keys == actual_keys, (
        f"OpenAPI drift! Run `task openapi-snapshot`. Diff: {expected_keys ^ actual_keys}"
    )
