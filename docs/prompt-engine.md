# Prompt Engine

flyquery's agent + pipeline prompts live as YAML files under
[`src/flyquery/resources/prompts/`](../src/flyquery/resources/prompts/).
This is byte-equivalent to the conventions in flycanon and flyradar
so the three services share one mental model for prompt tuning.

## Why YAML over Python strings

* **Operators tune prompts without a Python redeploy.** A devops
  engineer can edit a YAML file in a hotfix branch, run the
  smoke suite, and ship.
* **CI diffs prompts independently of code.** Reviewing a single
  YAML change is much faster than rereading a Python module to find
  the multi-paragraph triple-quoted string.
* **Long instructions stay out of code files.** YAML files have no
  line-length ceiling, so multi-paragraph prompts don't run into
  `ruff E501` warnings or get abbreviated to satisfy them.

## File layout

```
src/flyquery/resources/prompts/
├── grounding.yaml            # GroundingAgent
├── generation.yaml           # GenerationAgent
├── critic.yaml               # CriticAgent
├── explainer.yaml            # ExplainerAgent
├── describe.yaml             # DescribeAgent
├── relation_proposer.yaml    # RelationProposerAgent
├── rename_detection.yaml     # RenameDetectionAgent
└── column_name_proposer.yaml # ColumnNameProposerAgent
```

Each file declares (matching flycanon + flyradar):

```yaml
name: flyquery/<agent_name>
version: "1.0.0"
description: >-
  One-paragraph human description of what this agent does.

# Variables consumed by the user template (when present).

system: |
  System / instructions prompt -- passed to pydantic-ai's
  ``Agent.instructions``.

user: |  # optional
  Jinja2-templated user prompt:
  {{ question }}
  {% for h in hits -%}
  ...
  {% endfor %}
```

## Loader

[`src/flyquery/core/agents/prompt_loader.py`](../src/flyquery/core/agents/prompt_loader.py)
ships a 90-line loader that:

1. Reads the YAML file from the package resources.
2. Compiles the `user` template through Jinja2 with
   `StrictUndefined` (missing variables raise at the call site,
   not silently corrupt the prompt).
3. Exposes `.instructions` (the `system` block) + `.render(**vars)`
   (returns `(instructions, user_prompt)` tuple).

```python
from flyquery.core.agents.prompt_loader import load_prompt

prompt = load_prompt("grounding")
instructions, user = prompt.render(question="...", inv_tables=[...], ...)
```

Each `build_<agent>_agent` constructor loads its YAML and passes
`prompt.instructions` to `build_agent` -- there is **no** fallback
to inline Python strings.

## Editing a prompt

1. Edit the YAML file.
2. Bump `version` (semver) -- shows up in observability traces.
3. Run the unit tests:
   ```
   uv run pytest tests/unit/test_prompt_loader.py
   ```
   The grounding-anti-hallucination test catches accidental deletion
   of the Hard Rules.
4. Run the e2e demo (`scripts/nl_query_demo.py`) to verify the
   real LLM still produces grounded answers.

## Regression guards

`tests/unit/test_prompt_loader.py` pins:

* The loader resolves every shipped prompt name.
* `render` substitutes Jinja2 variables.
* `grounding.yaml` retains the hard rules against
  ``balance_sheet`` / ``income_statement`` / ``cash_flow`` /
  ``financials.*`` hallucinations.

If a prompt edit removes a rule, the test fails before the change
reaches main.
