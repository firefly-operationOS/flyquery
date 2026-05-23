# Copyright 2026 Firefly Software Solutions Inc
"""DI configuration bean for flyquery."""

from __future__ import annotations

from pyfly.container import configuration

from flyquery.config import FlyquerySettings


@configuration
class FlyqueryConfiguration:
    """Exposes :class:`FlyquerySettings` to the pyfly DI container."""

    def settings(self) -> FlyquerySettings:
        return FlyquerySettings()
