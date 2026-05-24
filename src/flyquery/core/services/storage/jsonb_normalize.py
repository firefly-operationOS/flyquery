# Copyright 2026 Firefly Software Solutions Inc
"""Canonical shape normalisation for JSONB columns.

Two columns on ``flyquery_schema_objects`` have a single intended
shape but historically saw drift:

* ``synonyms_json`` is canonically a ``list[str]`` (the SQLAlchemy
  entity declares ``Mapped[list]`` with a ``'[]'::jsonb`` default).
* ``governance_json`` is canonically a ``dict[str, Any]`` (entity:
  ``Mapped[dict | None]``).

Past bugs (chiefly ``NULL || dict`` jsonb concat without ``COALESCE``)
produced two-element arrays like ``[None, {...}]`` in ``governance_json``
that crashed the read endpoint with a Pydantic validation error.

The helpers in this module are the single coercion seam. Every
producer that builds an annotation dict and every DTO that
deserialises a JSONB row goes through them, so a polluted legacy
row never reaches the response.
"""

from __future__ import annotations

from typing import Any


def normalize_synonyms_json(value: Any) -> list[str]:
    """Coerce any historical shape to ``list[str]``.

    Accepts the canonical list, the legacy ``{"synonyms": [...]}``
    dict envelope, or ``None``. Anything else is best-effort
    stringified so a malformed row never breaks a response.
    """
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value if v is not None]
    if isinstance(value, dict):
        # Legacy envelope: ``{"synonyms": [...]}`` or a tag dict.
        inner = value.get("synonyms")
        if isinstance(inner, list):
            return [str(v) for v in inner if v is not None]
        return [str(v) for v in value.values() if isinstance(v, str)]
    return [str(value)]


def normalize_governance_json(value: Any) -> dict[str, Any]:
    """Coerce any historical shape to ``dict[str, Any]``.

    A list value is the fingerprint of the ``NULL || dict`` jsonb-concat
    bug: ``[null, {...}]``. We pick the rightmost dict element so the
    semantic-type / owner / policy keys survive.
    """
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, list):
        for item in reversed(value):
            if isinstance(item, dict):
                return item
        return {}
    return {}
