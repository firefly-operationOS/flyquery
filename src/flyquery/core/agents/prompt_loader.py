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

"""YAML+Jinja2 prompt loader, byte-equivalent to flycanon's convention.

flyquery's agent + pipeline prompts live as YAML files under
``flyquery/resources/prompts``. Each file declares (matching flycanon
+ flyradar byte-for-byte):

* ``system`` -- the agent instructions string. Surfaced as
  :attr:`PromptTemplate.instructions` in Python (pydantic-ai's
  ``instructions=`` parameter naming).
* ``user`` -- a Jinja2 template rendered per-call to produce the
  user prompt string for ``Agent.run``.
* ``name`` / ``version`` / ``description`` (optional) -- metadata.

Both ``system`` and ``user`` can reference Jinja2 variables. The
loader compiles templates once at startup and exposes a :meth:`render`
method callers use per request.

Why YAML over inline Python strings
-----------------------------------
* Operators tune prompts without redeploying Python code.
* CI can diff prompt changes independently of code changes.
* The pattern matches flycanon + flyradar so the three services
  share a single mental model.
* Long prompt strings stop polluting code files + ``ruff E501``.

The loader is intentionally minimal -- it does NOT auto-discover
files; the caller passes a known name. Unknown names raise
``PromptNotFoundError`` at startup, never at request time.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib.resources import files
from typing import Any

import yaml
from jinja2 import Environment, StrictUndefined


class PromptNotFoundError(LookupError):
    """Raised when ``load_prompt(name)`` can't find ``<name>.yaml``."""


@dataclass(slots=True)
class PromptTemplate:
    """Compiled prompt: instructions string + user-template renderer."""

    name: str
    instructions: str
    user_template: str
    description: str = ""

    def render(self, **variables: Any) -> tuple[str, str]:
        """Return ``(instructions, user_prompt)`` for one agent call.

        Both pieces support Jinja2 placeholders so a single template
        can adapt to per-request context. ``StrictUndefined`` is used
        on purpose -- silent fallbacks on missing variables produce
        confusing prompts; an explicit error surfaces the integration
        bug at the call site.
        """
        env = Environment(
            undefined=StrictUndefined,
            trim_blocks=True,
            lstrip_blocks=True,
            autoescape=False,
        )
        instructions = env.from_string(self.instructions).render(**variables)
        user_prompt = env.from_string(self.user_template).render(**variables)
        return instructions, user_prompt

    def render_user(self, **variables: Any) -> str:
        """Render only the user template (when the instructions are static)."""
        return self.render(**variables)[1]


def load_prompt(name: str) -> PromptTemplate:
    """Load ``flyquery/resources/prompts/<name>.yaml`` into a template.

    The YAML must declare ``system`` (agent instructions) + ``user``
    (Jinja2 template) keys, matching the flycanon + flyradar
    convention.

    Raises :class:`PromptNotFoundError` when the file doesn't exist;
    raises :class:`yaml.YAMLError` on a malformed file.
    """
    try:
        resource = files("flyquery.resources.prompts").joinpath(f"{name}.yaml")
        raw = resource.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise PromptNotFoundError(f"prompt {name!r} not found") from exc
    data = yaml.safe_load(raw) or {}
    return PromptTemplate(
        name=name,
        instructions=str(data.get("system") or ""),
        user_template=str(data.get("user") or ""),
        description=str(data.get("description") or ""),
    )
