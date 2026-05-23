# Copyright 2026 Firefly Software Solutions Inc
"""Presidio-backed PII scanner adapter.

Requires the [presidio] extra:
    pip install flyquery[presidio]
    # i.e.: presidio-analyzer + spacy model

If FLYQUERY_PII_SCANNER=presidio but the extra is not installed, the factory
raises ImportError loudly (per spec: fail loud, don't silently degrade).
"""

from __future__ import annotations

from flyquery.core.services.pii.scanner import PiiFinding, PiiTag


class PresidioPiiScanner:
    """Presidio AnalyzerEngine-backed adapter."""

    def __init__(self) -> None:
        try:
            from presidio_analyzer import AnalyzerEngine  # type: ignore[import-untyped]
        except ImportError as exc:
            raise ImportError(
                "FLYQUERY_PII_SCANNER=presidio requires the [presidio] extra. "
                "Install it with: pip install flyquery[presidio]"
            ) from exc
        self._engine = AnalyzerEngine()

    async def scan_single(self, value: str) -> PiiFinding | None:
        if not value:
            return None
        results = self._engine.analyze(text=value, language="en")
        if not results:
            return None
        # Return highest-score result
        best = max(results, key=lambda r: r.score)
        return PiiFinding(entity_type=best.entity_type, score=best.score)

    async def scan_column(
        self,
        name: str,
        description: str | None,
        samples: list[str],
        data_type: str,
    ) -> PiiTag | None:
        hits: dict[str, float] = {}
        # Scan column name itself
        name_results = self._engine.analyze(text=name or "", language="en")
        for r in name_results:
            hits[r.entity_type] = max(hits.get(r.entity_type, 0.0), r.score)
        # Scan description
        if description:
            desc_results = self._engine.analyze(text=description, language="en")
            for r in desc_results:
                hits[r.entity_type] = max(hits.get(r.entity_type, 0.0), r.score)
        # Scan samples
        for sample in samples:
            sample_results = self._engine.analyze(text=str(sample), language="en")
            for r in sample_results:
                hits[r.entity_type] = max(hits.get(r.entity_type, 0.0), r.score)

        if not hits:
            return None
        top = max(hits, key=lambda k: hits[k])
        return PiiTag(tag=top, source="PRESIDIO")
