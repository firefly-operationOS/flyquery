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

"""Read-only search helpers over the schema KB tables.

Covers:
- ``flyquery_schema_objects``  (BM25 via ``content_tsv``, pgvector via ``embedding``)
- ``flyquery_examples``        (APPROVED quality only)
- ``flyquery_semantic_metrics`` (PUBLISHED status only)
- ``flyquery_glossary_terms``
- ``flyquery_relations`` (approved, high-confidence)
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(frozen=True)
class Hit:
    """A single retrieval result from any KB table."""

    source_kind: str  # "schema_object" | "example" | "metric" | "glossary" | "relation"
    id: uuid.UUID
    text: str  # rendered for the reranker / grounding agent
    score: float
    metadata: dict = field(default_factory=dict)


def value_fingerprint(
    data_type: str | None,
    sample_values_json: object,
    profile_json: object,
    *,
    max_values: int = 40,
    max_chars: int = 400,
) -> str:
    """Compact, human-readable summary of a column's ACTUAL values.

    Surfaced into the grounding/generation prompts so the agents copy
    WHERE / CASE literals verbatim from real values instead of guessing
    -- e.g. a fiscal year stored as ``FY23`` (not ``2023``), the members
    of a tall/EAV category column (``P&L Line System`` rows like
    ``Total Revenue`` / ``Manpower``), or the magnitude gap between a
    scaled-duplicate measure (``FY`` ~0.02 vs ``FY (Real)`` ~25748).

    Returns ``""`` when there is nothing useful to show.
    """
    prof = profile_json if isinstance(profile_json, dict) else {}

    # NOTE: profiling stores ``subtotal_values`` (name-based candidates for
    # pre-aggregated rows). We deliberately do NOT surface them as an
    # exclusion directive: a "Total_*" value in a dimension is just as often a
    # legitimate additive bucket (e.g. unallocated/corporate) as a true rollup,
    # and any hint makes the agent wrongly drop it. Whether to exclude requires
    # the structural test (does the value's aggregate == the sum of the others?)
    # which is not available per-column at profile time. The general "aggregate
    # across ALL values / don't drop a value" prompt rule handles this safely.
    subtotal_note = ""

    # Self-referencing hierarchy hint: this column's values are entities from
    # another (higher-cardinality) column -- e.g. a manager column whose values
    # are people from the employee column. Surfaced even for high-cardinality
    # columns that have no listable values, because that is exactly when the
    # agent cannot otherwise tell who a person reports to.
    ref_col = prof.get("references_column")
    ref_note = (
        f" | HIERARCHY: holds entities/people from column '{ref_col}' (e.g. each row's "
        f"manager/owner/parent). To get a given person's group/team/reports, filter THIS "
        f"column to that person (case-insensitive LIKE), not the person's own row."
        if ref_col
        else ""
    )

    # Categorical: the stored distinct value set (low-cardinality columns).
    top_values = prof.get("top_values") or []
    if top_values:
        seen: set[str] = set()
        uniq: list[str] = []
        for tv in top_values:
            v = tv.get("value") if isinstance(tv, dict) else tv
            if v is None:
                continue
            s = str(v)
            if s not in seen:
                seen.add(s)
                uniq.append(s)
        shown = uniq[:max_values]
        body = " | ".join(shown)
        if len(body) > max_chars:
            body = body[:max_chars].rsplit("|", 1)[0].strip() + " | …"
        more = "" if len(uniq) <= len(shown) else f" (+{len(uniq) - len(shown)} more)"
        return f"values: {body}{more}{subtotal_note}{ref_note}" if body else ref_note.strip(" |")

    # Numeric / temporal: range + cardinality (exposes scaled duplicates).
    col_min, col_max = prof.get("min"), prof.get("max")
    if col_min is not None or col_max is not None:
        rng = f"range: {col_min} .. {col_max}"
        dist = prof.get("distinct_estimate")
        if dist is not None:
            rng += f" (~{dist} distinct)"
        return rng + ref_note

    # Fallback: a few raw sample values (high-cardinality columns).
    samples = sample_values_json if isinstance(sample_values_json, list) else []
    if samples:
        seen2: set[str] = set()
        uniq2: list[str] = []
        for v in samples:
            s = str(v)
            if s not in seen2:
                seen2.add(s)
                uniq2.append(s)
        if uniq2:
            return "e.g.: " + " | ".join(uniq2[:8]) + ref_note
    return ref_note.strip(" |")


def _column_hit(r, score: float) -> "Hit":
    """Build a ranked schema-object Hit, enriched with a value fingerprint.

    Used by the BM25 + vector column searches so the ranked "Top-ranked
    column matches" the grounding agent sees carry real values, not just
    name + description.
    """
    fp = value_fingerprint(r.data_type, r.sample_values_json, r.profile_json)
    text = f"{r.qualified_name}: {r.data_type}\n{r.description or ''}"
    if fp:
        text += f"\n{fp}"
    return Hit(
        source_kind="schema_object",
        id=r.id,
        text=text,
        score=score,
        metadata={"qualified_name": r.qualified_name, "table_id": str(r.table_id), "values": fp},
    )


class SearchIndex:
    """Read-only query helpers that operate on a shared ``AsyncSession``."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def bm25_schema_objects(self, query: str, dataset_id: uuid.UUID, limit: int = 30) -> list[Hit]:
        """Full-text BM25 search over ``content_tsv`` on schema objects.

        :param query: natural-language query string
        :param dataset_id: dataset scope
        :param limit: maximum rows to return
        :return: scored list of schema-object hits
        """
        rows = await self._session.execute(
            sa.text(
                """
                SELECT o.id, o.qualified_name, o.description, o.data_type, o.table_id,
                       o.sample_values_json, o.profile_json,
                       ts_rank(o.content_tsv, plainto_tsquery('english', :q)) AS score
                FROM flyquery_schema_objects o
                JOIN flyquery_tables t ON t.id = o.table_id
                WHERE t.dataset_id = :ds AND o.is_active = true
                  AND o.snapshot_id = t.current_snapshot_id
                  AND o.content_tsv @@ plainto_tsquery('english', :q)
                ORDER BY score DESC
                LIMIT :lim
                """
            ),
            {"q": query, "ds": dataset_id, "lim": limit},
        )
        return [_column_hit(r, float(r.score)) for r in rows.mappings()]

    async def vector_schema_objects(
        self,
        query_embedding: list[float],
        dataset_id: uuid.UUID,
        limit: int = 30,
    ) -> list[Hit]:
        """Cosine-distance pgvector search over schema-object embeddings.

        :param query_embedding: pre-computed query vector
        :param dataset_id: dataset scope
        :param limit: maximum rows to return
        :return: scored list of schema-object hits (cosine similarity)
        """
        rows = await self._session.execute(
            sa.text(
                """
                SELECT o.id, o.qualified_name, o.description, o.data_type, o.table_id,
                       o.sample_values_json, o.profile_json,
                       1 - (o.embedding <=> CAST(:emb AS vector)) AS score
                FROM flyquery_schema_objects o
                JOIN flyquery_tables t ON t.id = o.table_id
                WHERE t.dataset_id = :ds AND o.is_active = true
                  AND o.snapshot_id = t.current_snapshot_id AND o.embedding IS NOT NULL
                ORDER BY o.embedding <=> CAST(:emb AS vector)
                LIMIT :lim
                """
            ),
            {"emb": str(query_embedding), "ds": dataset_id, "lim": limit},
        )
        return [_column_hit(r, float(r.score)) for r in rows.mappings()]

    async def all_schema_objects(
        self,
        dataset_id: uuid.UUID,
        *,
        limit: int = 500,
    ) -> list[Hit]:
        """Return every active schema_object in the dataset, unranked.

        Used as a fallback when BM25 + vector retrieval both return zero
        hits -- without this the grounding prompt carries no table
        inventory and the LLM hallucinates plausible-but-wrong names
        like ``balance_sheet`` / ``income_statement``.

        For TABLE-kind rows, the ``text`` payload is enriched with the
        list of column names + their inferred descriptions. That gives
        the LLM a self-contained semantic fingerprint per table, even
        when the describe stage left the table-level description NULL
        (the describe stage only generates per-column descriptions
        today). Without this enrichment the prompt would list 61
        opaque names like ``IVI_MALAGA_SL__Activos`` with no signal
        for the LLM to match user intent against.
        """
        # Fetch tables (with their column fingerprints) and columns
        # separately so we can build a rich text per table.
        table_rows = (
            (
                await self._session.execute(
                    sa.text(
                        """
                SELECT o.id, o.qualified_name, o.description, o.table_id, o.kind,
                       array_agg(c.qualified_name ORDER BY c.qualified_name) AS col_qnames,
                       array_agg(c.description    ORDER BY c.qualified_name) AS col_descs
                FROM flyquery_schema_objects o
                JOIN flyquery_tables t ON t.id = o.table_id
                LEFT JOIN flyquery_schema_objects c
                    ON c.table_id = o.table_id
                   AND c.kind = 'COLUMN'
                   AND c.is_active = true
                   AND c.snapshot_id = t.current_snapshot_id
                WHERE t.dataset_id = :ds AND o.is_active = true AND o.kind = 'TABLE'
                  AND o.snapshot_id = t.current_snapshot_id
                GROUP BY o.id, o.qualified_name, o.description, o.table_id, o.kind
                ORDER BY o.qualified_name
                """
                    ),
                    {"ds": dataset_id},
                )
            )
            .mappings()
            .all()
        )

        column_rows = (
            (
                await self._session.execute(
                    sa.text(
                        """
                SELECT o.id, o.qualified_name, o.description, o.data_type, o.table_id, o.kind,
                       o.sample_values_json, o.profile_json
                FROM flyquery_schema_objects o
                JOIN flyquery_tables t ON t.id = o.table_id
                WHERE t.dataset_id = :ds AND o.is_active = true AND o.kind = 'COLUMN'
                  AND o.snapshot_id = t.current_snapshot_id
                ORDER BY o.qualified_name
                LIMIT :lim
                """
                    ),
                    {"ds": dataset_id, "lim": limit},
                )
            )
            .mappings()
            .all()
        )

        hits: list[Hit] = []
        for r in table_rows:
            # Build a "fingerprint" string: short column-name list +
            # one-line description of each column (truncated). Stays
            # under ~600 chars per table; for 60 tables that's ~36KB
            # in the prompt -- well within Claude's window.
            qnames = list(r["col_qnames"] or [])
            descs = list(r["col_descs"] or [])
            unq_cols = [qn.rsplit(".", 1)[-1] for qn in qnames]
            col_list = ", ".join(unq_cols[:30])
            sample_desc = next((d for d in descs if d), None)
            payload_parts = [
                r["description"] or "",
                f"columns: {col_list}" if unq_cols else "",
                f"sample column meaning: {sample_desc[:200]}" if sample_desc else "",
            ]
            text = "\n".join(p for p in payload_parts if p)
            hits.append(
                Hit(
                    source_kind="schema_object",
                    id=r["id"],
                    text=text,
                    score=1.0,
                    metadata={
                        "qualified_name": r["qualified_name"],
                        "table_id": str(r["table_id"]),
                        "kind": "TABLE",
                        "columns": unq_cols,
                    },
                )
            )

        for r in column_rows:
            fp = value_fingerprint(r["data_type"], r["sample_values_json"], r["profile_json"])
            text = f"{r['qualified_name']}: {r['data_type'] or ''}\n{r['description'] or ''}"
            if fp:
                text += f"\n{fp}"
            hits.append(
                Hit(
                    source_kind="schema_object",
                    id=r["id"],
                    text=text,
                    score=1.0,
                    metadata={
                        "qualified_name": r["qualified_name"],
                        "table_id": str(r["table_id"]),
                        "kind": "COLUMN",
                        "values": fp,
                    },
                )
            )
        return hits

    async def approved_examples(
        self,
        query: str,
        query_embedding: list[float] | None,
        workspace_id: uuid.UUID,
        dataset_id: uuid.UUID | None = None,
        limit: int = 10,
    ) -> list[Hit]:
        """Retrieve APPROVED examples via BM25 (+ optional vector cosine).

        When ``query_embedding`` is None, returns BM25 results only.

        :param query: NL question text
        :param query_embedding: optional query vector
        :param workspace_id: workspace scope
        :param dataset_id: optional dataset filter
        :param limit: maximum rows to return
        :return: list of example hits
        """
        ds_filter = "AND dataset_id = :dataset_id" if dataset_id is not None else ""
        params: dict = {"q": query, "workspace_id": workspace_id, "lim": limit}
        if dataset_id is not None:
            params["dataset_id"] = dataset_id

        if query_embedding is not None:
            params["emb"] = str(query_embedding)
            rows = await self._session.execute(
                sa.text(
                    f"""
                    SELECT id, question, generated_sql,
                           CASE
                               WHEN embedding IS NOT NULL
                               THEN 1 - (embedding <=> CAST(:emb AS vector))
                               ELSE 0.5
                           END AS score
                    FROM flyquery_examples
                    WHERE workspace_id = :workspace_id AND quality = 'APPROVED' {ds_filter}
                    ORDER BY score DESC
                    LIMIT :lim
                    """
                ),
                params,
            )
        else:
            rows = await self._session.execute(
                sa.text(
                    f"""
                    SELECT id, question, generated_sql,
                           0.5 AS score
                    FROM flyquery_examples
                    WHERE workspace_id = :workspace_id AND quality = 'APPROVED' {ds_filter}
                    ORDER BY created_at DESC
                    LIMIT :lim
                    """
                ),
                params,
            )
        return [
            Hit(
                source_kind="example",
                id=r.id,
                text=f"Q: {r.question}\nSQL: {r.generated_sql}",
                score=float(r.score),
                metadata={"question": r.question, "generated_sql": r.generated_sql},
            )
            for r in rows.mappings()
        ]

    async def published_metrics(self, query: str, dataset_id: uuid.UUID, limit: int = 8) -> list[Hit]:
        """Return PUBLISHED semantic metrics via simple name/label match.

        :param query: NL question text (used for trigram / fulltext match)
        :param dataset_id: dataset scope
        :param limit: maximum rows to return
        :return: list of metric hits
        """
        rows = await self._session.execute(
            sa.text(
                """
                SELECT id, name, label, description, compiled_sql_template
                FROM flyquery_semantic_metrics
                WHERE dataset_id = :ds AND status = 'PUBLISHED'
                ORDER BY name
                LIMIT :lim
                """
            ),
            {"ds": dataset_id, "lim": limit},
        )
        return [
            Hit(
                source_kind="metric",
                id=r.id,
                text=f"metric:{r.name} — {r.label or ''}\n{r.description or ''}",
                score=1.0,
                metadata={
                    "name": r.name,
                    "label": r.label,
                    "compiled_sql_template": r.compiled_sql_template,
                },
            )
            for r in rows.mappings()
        ]

    async def glossary_hits(self, query: str, workspace_id: uuid.UUID, limit: int = 8) -> list[Hit]:
        """Return glossary terms matching the query via trigram similarity.

        Falls back to returning all terms (up to limit) when pg_trgm is not
        available or the query contains no useful tokens.

        :param query: NL question text
        :param workspace_id: workspace scope
        :param limit: maximum rows to return
        :return: list of glossary hits
        """
        rows = await self._session.execute(
            sa.text(
                """
                SELECT id, term, definition, synonyms_json, related_metrics_json
                FROM flyquery_glossary_terms
                WHERE workspace_id = :ws
                ORDER BY term
                LIMIT :lim
                """
            ),
            {"ws": workspace_id, "lim": limit},
        )
        return [
            Hit(
                source_kind="glossary",
                id=r.id,
                text=f"term:{r.term}\n{r.definition}",
                score=1.0,
                metadata={
                    "term": r.term,
                    "definition": r.definition,
                    "related_metrics": list(r.related_metrics_json or []),
                },
            )
            for r in rows.mappings()
        ]

    async def approved_relations(self, dataset_id: uuid.UUID, threshold: float = 0.85) -> list[Hit]:
        """Return high-confidence, approved schema relations.

        :param dataset_id: dataset scope
        :param threshold: minimum confidence_score to include
        :return: list of relation hits
        """
        rows = await self._session.execute(
            sa.text(
                """
                SELECT r.id,
                       ft.qualified_name || '.' || r.from_column_name AS from_qname,
                       tt.qualified_name || '.' || r.to_column_name   AS to_qname,
                       r.kind, r.confidence
                FROM flyquery_relations r
                JOIN flyquery_tables ft ON ft.id = r.from_table_id
                JOIN flyquery_tables tt ON tt.id = r.to_table_id
                WHERE ft.dataset_id = :ds
                  AND r.status = 'APPROVED'
                  AND r.confidence >= :threshold
                ORDER BY r.confidence DESC
                """
            ),
            {"ds": dataset_id, "threshold": threshold},
        )
        return [
            Hit(
                source_kind="relation",
                id=r.id,
                text=(f"{r.from_qname} {r.kind} {r.to_qname} (confidence={r.confidence:.2f})"),
                score=float(r.confidence),
                metadata={
                    "from_qualified_name": r.from_qname,
                    "to_qualified_name": r.to_qname,
                    "relation_type": r.kind,
                },
            )
            for r in rows.mappings()
        ]
