# Copyright 2026 Firefly Software Solutions Inc
"""PyFly application entry point for flyquery.

``scan_packages`` declares every package containing ``@configuration``,
``@rest_controller``, ``@service``, ``@command_handler``,
``@query_handler``, or ``@repository`` beans so pyfly's DI container
can discover them at boot.

Exception handlers are registered explicitly via
``flyquery.web.conventions.register_exception_handlers(app)`` in
``flyquery.main`` -- pyfly's FastAPI adapter does not scan
``@controller_advice`` beans, so the conventions handler table is
hand-wired against the FastAPI app.
"""

from __future__ import annotations

from pyfly.core import pyfly_application
from pyfly.starters.core import enable_core_stack


@enable_core_stack
@pyfly_application(
    name="flyquery",
    version="26.5.0",
    description=(
        "flyquery -- Operational Structured-Data Intelligence "
        "(upload-driven). Multi-tenant ingestion + Text-to-SQL "
        "over user-uploaded structured files. Part of Firefly "
        "OperationOS."
    ),
    scan_packages=[
        "flyquery.core",  # @configuration class
        "flyquery.core.services",  # CQRS handlers + @service beans
        "flyquery.web.controllers",  # REST controllers (user-tier)
        "flyquery.web.controllers.agent",  # REST controllers (agent-tier)
    ],
)
class FlyqueryApplication:
    """Marker class consumed by :class:`PyFlyApplication` at boot."""
