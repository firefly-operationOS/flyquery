#!/usr/bin/env python
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

"""Generate the synthetic example fixtures under ``examples/``.

Produces realistic business data across every format the ingest pipeline
supports. Re-runnable -- overwrites the existing files.

Fixtures
--------
* ``examples/csv/sales_orders.csv``   -- 500-row, 9-col orders table
* ``examples/csv/customers.csv``      -- 120-row customer dimension
* ``examples/json/products.json``     -- array-of-objects product catalogue
* ``examples/jsonl/events.jsonl``     -- line-delimited event log (1500 rows)
* ``examples/xlsx/sales_orders.xlsx`` -- clean tabular workbook (same 500 rows)
* ``examples/xlsx/financials_dashboard.xlsx`` -- dashboard-style BvD-like
  XLSX with multiple sections that DuckDB sniffing cannot auto-detect.
* ``examples/parquet/transactions.parquet`` -- 2000-row transactions table

Each file is deterministic (seeded RNG) so CI snapshots stay stable.
"""

from __future__ import annotations

import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EX = ROOT / "examples"

# Reproducible business data
RNG = random.Random(20260524)


def _customers(n: int) -> list[dict]:
    first = [
        "Ana",
        "Bruno",
        "Clara",
        "Diego",
        "Elena",
        "Federico",
        "Gabriela",
        "Hugo",
        "Ines",
        "Javier",
        "Karla",
        "Luis",
        "Marta",
        "Nicolas",
        "Olivia",
    ]
    last = ["Garcia", "Lopez", "Martinez", "Sanchez", "Romero", "Diaz", "Torres", "Ruiz", "Vargas", "Castro"]
    countries = ["ES", "FR", "DE", "IT", "PT", "GB", "US", "MX", "AR", "BR"]
    tiers = ["bronze", "silver", "gold", "platinum"]
    rows: list[dict] = []
    for i in range(n):
        rows.append(
            {
                "customer_id": f"CUST-{1000 + i:04d}",
                "name": f"{RNG.choice(first)} {RNG.choice(last)}",
                "email": f"cust{1000 + i}@example.com",
                "country_code": RNG.choice(countries),
                "tier": RNG.choices(tiers, weights=[40, 30, 20, 10])[0],
                "lifetime_value_eur": round(RNG.uniform(50, 25_000), 2),
                "signup_date": (date(2020, 1, 1) + timedelta(days=RNG.randint(0, 1500))).isoformat(),
                "is_active": RNG.random() < 0.85,
            }
        )
    return rows


def _orders(n: int, customers: list[dict]) -> list[dict]:
    products = ["Pro Plan", "Team Plan", "Enterprise", "Add-on Seat", "Storage GB", "Training", "Support"]
    rows: list[dict] = []
    for i in range(n):
        cust = RNG.choice(customers)
        qty = RNG.randint(1, 10)
        unit = round(RNG.uniform(15, 500), 2)
        rows.append(
            {
                "order_id": f"ORD-{50000 + i:06d}",
                "customer_id": cust["customer_id"],
                "country_code": cust["country_code"],
                "product": RNG.choice(products),
                "quantity": qty,
                "unit_price_eur": unit,
                "amount_eur": round(qty * unit, 2),
                "order_date": (date(2024, 1, 1) + timedelta(days=RNG.randint(0, 600))).isoformat(),
                "status": RNG.choices(
                    ["paid", "shipped", "refunded", "cancelled", "pending"],
                    weights=[55, 30, 5, 5, 5],
                )[0],
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"  wrote {path.relative_to(ROOT)}  rows={len(rows)}")


def write_json(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, indent=2, default=str), encoding="utf-8")
    print(f"  wrote {path.relative_to(ROOT)}  rows={len(rows)}")


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, default=str) + "\n")
    print(f"  wrote {path.relative_to(ROOT)}  rows={len(rows)}")


def write_xlsx_clean(path: Path, rows: list[dict]) -> None:
    """Standard tabular XLSX -- one sheet, first row is the header."""
    try:
        from openpyxl import Workbook
    except ImportError:
        print("  SKIP openpyxl not installed; pip install openpyxl")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = "orders"
    cols = list(rows[0].keys())
    ws.append(cols)
    for r in rows:
        ws.append([r[c] for c in cols])
    wb.save(path)
    print(f"  wrote {path.relative_to(ROOT)}  rows={len(rows)}")


def write_xlsx_dashboard(path: Path) -> None:
    """Dashboard-style XLSX -- multiple sections separated by blank rows.

    Exercises the section-detector + smart column-name proposer +
    pseudo-header detector. Mirrors the BvD / Orbis export shape that
    triggered all the section-extraction work in May 2026.
    """
    try:
        from openpyxl import Workbook
    except ImportError:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    ws = wb.active
    ws.title = "Financials"

    # Title band
    ws.append(["ACME WIDGETS SL"])
    ws.append(["Financial Summary -- generated by flyquery example generator"])
    ws.append([])

    # Section 1: Balance Sheet (Activos)
    ws.append(["Activos"])
    ws.append(["", "2019", "2020", "2021", "2022", "2023"])
    ws.append(["Activos fijos", 320_000, 410_000, 502_000, 615_000, 740_000])
    ws.append(["Activo circulante", 180_000, 215_000, 260_000, 310_000, 380_000])
    ws.append(["Activos totales", 500_000, 625_000, 762_000, 925_000, 1_120_000])
    ws.append([])

    # Section 2: Profit & Loss with numeric pseudo-header row
    ws.append(["Cuenta de Pérdidas y Ganancias"])
    ws.append([])  # DuckDB will sniff the values row as the header
    ws.append(["Revenue", 850_000, 1_020_000, 1_245_000, 1_460_000, 1_720_000])
    ws.append(["COGS", -340_000, -395_000, -465_000, -540_000, -622_000])
    ws.append(["Gross Profit", 510_000, 625_000, 780_000, 920_000, 1_098_000])
    ws.append(["OpEx", -380_000, -430_000, -495_000, -555_000, -612_000])
    ws.append(["EBIT", 130_000, 195_000, 285_000, 365_000, 486_000])
    ws.append([])

    # Section 3: Ratios
    ws.append(["Ratios principales"])
    ws.append(["Indicator", "yr1", "yr2", "yr3", "yr4", "yr5"])
    ws.append(["ROE %", 18.4, 22.1, 24.5, 26.0, 28.7])
    ws.append(["ROA %", 12.0, 14.2, 16.1, 17.8, 19.5])
    ws.append(["Gross %", 60.0, 61.3, 62.7, 63.0, 63.8])

    wb.save(path)
    print(f"  wrote {path.relative_to(ROOT)}  sections=3")


def write_parquet(path: Path, rows: list[dict]) -> None:
    try:
        import pyarrow as pa
        import pyarrow.parquet as pq
    except ImportError:
        print("  SKIP pyarrow not installed")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    cols: dict[str, list] = {k: [] for k in rows[0]}
    for r in rows:
        for k in cols:
            cols[k].append(r[k])
    pq.write_table(pa.table(cols), path)
    print(f"  wrote {path.relative_to(ROOT)}  rows={len(rows)}")


def main() -> int:
    EX.mkdir(exist_ok=True)
    print("=== generating fixtures ===")

    custs = _customers(120)
    orders = _orders(500, custs)

    write_csv(EX / "csv" / "customers.csv", custs)
    write_csv(EX / "csv" / "sales_orders.csv", orders)
    write_json(
        EX / "json" / "products.json",
        [
            {
                "product_id": f"PROD-{i:03d}",
                "name": n,
                "category": c,
                "list_price_eur": round(RNG.uniform(20, 800), 2),
                "in_stock": RNG.randint(0, 1500),
            }
            for i, (n, c) in enumerate(
                [
                    ("Pro Plan", "subscription"),
                    ("Team Plan", "subscription"),
                    ("Enterprise", "subscription"),
                    ("Add-on Seat", "addon"),
                    ("Storage GB", "addon"),
                    ("Training", "service"),
                    ("Support", "service"),
                    ("Onboarding Pack", "service"),
                    ("API Quota +", "addon"),
                    ("White Label", "addon"),
                ]
                * 5
            )
        ],
    )
    write_jsonl(
        EX / "jsonl" / "events.jsonl",
        [
            {
                "event_id": f"EVT-{i:07d}",
                "occurred_at": (date(2024, 1, 1) + timedelta(days=RNG.randint(0, 600))).isoformat(),
                "user_id": f"USR-{RNG.randint(1, 5000):05d}",
                "event_type": RNG.choices(
                    ["page_view", "click", "signup", "purchase", "logout", "error"],
                    weights=[40, 30, 5, 8, 12, 5],
                )[0],
                "duration_ms": RNG.randint(20, 30_000),
                "country_code": RNG.choice(["ES", "FR", "DE", "GB", "US"]),
            }
            for i in range(1500)
        ],
    )
    write_xlsx_clean(EX / "xlsx" / "sales_orders.xlsx", orders)
    write_xlsx_dashboard(EX / "xlsx" / "financials_dashboard.xlsx")
    write_parquet(
        EX / "parquet" / "transactions.parquet",
        [
            {
                "txn_id": f"TXN-{i:08d}",
                "account_id": f"ACCT-{RNG.randint(1, 250):04d}",
                "amount_eur": round(RNG.uniform(-2500, 5000), 2),
                "currency_code": RNG.choice(["EUR", "USD", "GBP"]),
                "merchant": RNG.choice(["AMZN", "ALSA", "MERCADONA", "CARREFOUR", "STRIPE", "ZARA"]),
                "posted_at": (date(2024, 1, 1) + timedelta(days=RNG.randint(0, 600))).isoformat(),
            }
            for i in range(2000)
        ],
    )
    print("done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
