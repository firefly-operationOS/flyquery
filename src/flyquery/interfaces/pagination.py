# Copyright 2026 Firefly Software Solutions Inc
"""Generic pagination envelope used by every list endpoint.

The flyquery REST surface used to ship three different list shapes:

1. ``{items, total, limit, offset, has_more}`` -- datasets, workspaces,
   tables (search), ingest-jobs.
2. ``{items}`` only -- conversations, glossary, examples, semantic
   metrics, semantic dimensions, snapshots, schema objects, schema
   changes, relations, agent-tokens, version history.
3. Bare ``list`` returns -- a few edge cases (agent-tokens list).

The first form lets consumers paginate and tell "this is the last
page" from "I got 0 items by coincidence"; the second + third don't.
Both generated SDKs (Python + Java) modelled them with three or four
different envelope shapes, which forced callers into a lot of
``isinstance`` checks.

:class:`Paginated` is the single shape now. Every list endpoint
returns it. Fields beyond ``items`` are optional so endpoints whose
underlying service doesn't know the total (e.g. cheap listings that
intentionally cap at 200 rows without a COUNT(*)) can leave ``total``
unset and consumers fall back to ``has_more`` for "is there more to
fetch?". Endpoints with cheap counts populate every field.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class Paginated(BaseModel, Generic[T]):  # noqa: UP046  -- PEP 695 generics break openapi-generator's schema introspection
    """Uniform list-endpoint envelope.

    Fields
    ------
    items:
        The page of records. Always present (may be empty).
    total:
        Total number of records matching the query, ignoring
        pagination. ``None`` when the underlying service cannot
        cheaply compute it -- consumers should use ``has_more`` to
        decide whether to keep paging.
    limit:
        Page size that was applied. ``None`` if the endpoint does not
        paginate (returns "all of them" by design).
    offset:
        Offset that was applied. ``None`` for non-paginating endpoints.
    has_more:
        ``True`` when at least one more page exists, ``False`` when the
        caller has reached the end. Always set when ``limit`` is set;
        ``None`` for non-paginating endpoints.
    """

    model_config = ConfigDict(frozen=True)

    items: list[T] = Field(default_factory=list)
    total: int | None = None
    limit: int | None = None
    offset: int | None = None
    has_more: bool | None = None

    @classmethod
    def of(
        cls,
        items: list[T],
        *,
        total: int | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> Paginated[T]:
        """Construct a :class:`Paginated` envelope with auto-computed ``has_more``.

        ``has_more`` is derived as ``(offset + len(items)) < total``
        when both ``offset`` and ``total`` are known. When ``total``
        is unknown but ``limit`` is, we assume the caller asked for
        ``limit`` rows and received fewer than that -> no more pages
        (best-effort heuristic that mirrors what every existing
        controller already does).
        """
        if total is not None and offset is not None:
            has_more = (offset + len(items)) < total
        elif limit is not None:
            has_more = len(items) >= limit
        else:
            has_more = None
        return cls(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
            has_more=has_more,
        )


__all__ = ["Paginated"]
