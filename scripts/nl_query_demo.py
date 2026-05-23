#!/usr/bin/env python
# Copyright 2026 Firefly Software Solutions Inc
"""Natural-language query demo against a running flyquery instance.

Asks 6 questions in plain prose -- no table names, no column names --
and pretty-prints the full pipeline response (SQL, rows, explanation).

Reads tenant / workspace / dataset config from CLI args and
``FLYQUERY_BASE_URL`` (default ``http://127.0.0.1:8520``).

Local debug script -- excluded from the repo via .gitignore's
``scripts/probe_*.py`` / ``scripts/_local_*.py`` patterns.
"""

from __future__ import annotations

import json
import os
import sys

import httpx


def ask(base: str, headers: dict, dataset_id: str, question: str) -> dict:
    r = httpx.post(
        f"{base}/api/v1/query",
        headers=headers,
        json={"question": question, "dataset_id": dataset_id},
        timeout=120.0,
    )
    return r.json()


def pretty(question: str, resp: dict) -> None:
    bar = "═" * 78
    print(f"\n{bar}\n▶ {question}\n{bar}")
    if "error" in resp:
        print(f"  ERROR: {resp['error'].get('message')}")
        return
    print(f"  execution_status: {resp.get('execution_status')}")
    print(f"  elapsed_ms:       {resp.get('elapsed_ms')}")
    sql = (resp.get("sql") or "").strip()
    print("  SQL:")
    for line in sql.split("\n"):
        print(f"      {line}")
    preview = resp.get("preview") or []
    print(f"  rows: {len(preview)}")
    for r in preview[:6]:
        print(f"    - {r}")
    if len(preview) > 6:
        print(f"    … and {len(preview) - 6} more rows")
    exp = (resp.get("explanation") or "").strip()
    print("  ─── EXPLANATION ───")
    if exp:
        for line in exp.split("\n"):
            print(f"  {line}")
    else:
        print("  (no explanation -- pipeline failure or empty result)")


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: nl_query_demo.py <workspace_id> <dataset_id>", file=sys.stderr)
        return 2
    base = os.environ.get("FLYQUERY_BASE_URL", "http://127.0.0.1:8520")
    ws = sys.argv[1]
    ds = sys.argv[2]
    headers = {"X-Tenant-Id": "demo", "X-Workspace-Id": ws}

    questions = [
        "What is the company's total assets and how have they evolved over the years?",
        "Tell me about the company's financial performance -- what does the income statement look like?",
        "Who are the major shareholders of this company?",
        "What sector does the company operate in?",
        "What was the company's profit or loss in the most recent year compared to a few years ago?",
        "Is this company financially healthy? Give me a summary based on the data.",
    ]
    for q in questions:
        try:
            resp = ask(base, headers, ds, q)
        except httpx.HTTPError as exc:
            print(f"  HTTP error: {exc}")
            continue
        pretty(q, resp)
        # Save raw JSON for later inspection.
        with open(f"/tmp/nl_{hash(q) & 0xFFFFFF:06x}.json", "w") as f:
            json.dump(resp, f, indent=2, default=str)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
