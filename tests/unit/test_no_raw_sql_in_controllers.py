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

"""CI gate -- fail the build if any controller calls ``sa.text(...)``.

Raw SQL lives in dedicated ``@repository`` beans, never in
``src/flyquery/web/controllers/``. This test pins that invariant so a
future PR cannot silently bring raw SQL back into the HTTP layer.

If you legitimately need to write SQL from a controller, the answer
is almost always "extract it into a repository under
``src/flyquery/core/services/{domain}/{domain}_repository.py``".

Controllers are still allowed to import ``async_sessionmaker`` /
``AsyncSession`` because they sometimes need to pass them through
to services that own per-request session lifecycle (the query +
sql_execute paths build a fresh ``SearchIndex`` / ``TableResolver``
per request -- those need a live session). The gate is therefore
narrow: only ``sa.text(`` / ``sqlalchemy.text(`` calls are forbidden.
"""

from __future__ import annotations

import re
from pathlib import Path

_CONTROLLERS_DIR = Path(__file__).resolve().parents[2] / "src/flyquery/web/controllers"

# Match ``sa.text(`` and ``sqlalchemy.text(`` (with optional whitespace).
_RAW_SQL_RE = re.compile(r"\b(?:sa|sqlalchemy)\.text\s*\(")


def test_no_controller_invokes_sa_text() -> None:
    """No controller file may call ``sa.text(...)`` directly."""
    violations: list[str] = []
    for path in sorted(_CONTROLLERS_DIR.rglob("*.py")):
        # Skip __init__ + __pycache__ as a defensive measure.
        if path.name == "__init__.py" or "__pycache__" in path.parts:
            continue
        source = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(source.splitlines(), start=1):
            # Strip comments before matching so a comment that
            # *mentions* sa.text doesn't trigger the gate.
            stripped = line.split("#", 1)[0]
            if _RAW_SQL_RE.search(stripped):
                rel = path.relative_to(_CONTROLLERS_DIR.parents[3])
                violations.append(f"{rel}:{lineno}: {line.strip()}")

    assert not violations, (
        "Raw SQL detected in controllers. Move it into a repository "
        "under src/flyquery/core/services/{domain}/{domain}_repository.py "
        "and call it from a service bean. See "
        "docs/superpowers/specs/refactor-repository-layer.md.\n\n" + "\n".join(violations)
    )


def test_no_controller_imports_sqlalchemy_module() -> None:
    """Controllers must not ``import sqlalchemy as sa`` or
    ``from sqlalchemy import ...``.

    The narrow ``from sqlalchemy.ext.asyncio import AsyncSession,
    async_sessionmaker`` is allowed -- those are type-only aliases
    threaded through to services. Anything that brings the SQL
    builder into the controller is rejected.
    """
    violations: list[str] = []
    bare_import_re = re.compile(r"^\s*(?:import sqlalchemy(?:\s+as\s+\w+)?$|from sqlalchemy import )")
    for path in sorted(_CONTROLLERS_DIR.rglob("*.py")):
        if path.name == "__init__.py" or "__pycache__" in path.parts:
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if bare_import_re.match(line):
                rel = path.relative_to(_CONTROLLERS_DIR.parents[3])
                violations.append(f"{rel}:{lineno}: {line.strip()}")
    assert not violations, (
        "Controllers must not import the SQL builder. Allowed: "
        "``from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker``. "
        "Forbidden: ``import sqlalchemy`` / ``from sqlalchemy import ...``.\n\n" + "\n".join(violations)
    )
