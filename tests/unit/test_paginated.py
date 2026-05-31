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

"""Unit tests for Paginated[T] -- the uniform list-endpoint envelope."""

from __future__ import annotations

from pydantic import BaseModel

from flyquery.interfaces.pagination import Paginated


class _Item(BaseModel):
    id: int
    name: str


def _items(n: int) -> list[_Item]:
    return [_Item(id=i, name=f"row-{i}") for i in range(n)]


def test_of_with_total_computes_has_more_true_when_more_pages_remain() -> None:
    env = Paginated.of(_items(10), total=100, limit=10, offset=0)
    assert env.items == _items(10)
    assert env.total == 100
    assert env.limit == 10
    assert env.offset == 0
    assert env.has_more is True


def test_of_with_total_computes_has_more_false_on_last_page() -> None:
    env = Paginated.of(_items(7), total=27, limit=10, offset=20)
    assert env.has_more is False  # 20 + 7 == 27 -> last page


def test_of_with_total_zero_is_empty_and_terminal() -> None:
    env = Paginated.of([], total=0, limit=10, offset=0)
    assert env.items == []
    assert env.total == 0
    assert env.has_more is False


def test_of_without_total_falls_back_to_limit_heuristic() -> None:
    """When the service doesn't know total but limit is set, infer
    has_more from whether we got a full page."""
    # Full page of 50 -> assume more might exist.
    env = Paginated.of(_items(50), limit=50)
    assert env.total is None
    assert env.has_more is True
    # Partial page -> definitely no more.
    env = Paginated.of(_items(7), limit=50)
    assert env.has_more is False


def test_of_with_no_pagination_metadata_leaves_has_more_none() -> None:
    """Non-paginating endpoint -> has_more is undefined."""
    env = Paginated.of(_items(3))
    assert env.total is None
    assert env.limit is None
    assert env.offset is None
    assert env.has_more is None


def test_of_serialises_to_json_with_expected_shape() -> None:
    env = Paginated.of(_items(3), total=3, limit=50, offset=0)
    dumped = env.model_dump(mode="json")
    assert dumped == {
        "items": [{"id": 0, "name": "row-0"}, {"id": 1, "name": "row-1"}, {"id": 2, "name": "row-2"}],
        "total": 3,
        "limit": 50,
        "offset": 0,
        "has_more": False,
    }


def test_default_constructor_yields_empty_envelope() -> None:
    env: Paginated[_Item] = Paginated()
    assert env.items == []
    assert env.total is None
    assert env.has_more is None


def test_envelope_is_immutable() -> None:
    """``frozen=True`` -- attribute reassignment must raise."""
    env = Paginated.of(_items(3), total=3, limit=10, offset=0)
    try:
        env.total = 99  # type: ignore[misc]
    except Exception:  # noqa: BLE001 -- pydantic raises ValidationError
        return
    raise AssertionError("Paginated should be frozen")
