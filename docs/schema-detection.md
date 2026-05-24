# Schema Detection in flyquery

## TL;DR

flyquery turns an opaque blob of bytes into a typed, described, embedded
schema in 10 deterministic stages. Format is decided by file extension first
(magic bytes only as a tiebreaker), `.gz` / `.bz2` / `.zip` wrappers are
stripped recursively, and each format hands off to a dedicated reader that
materialises the data into snappy-compressed Parquet under the dataset's
object-store prefix. Type inference is **DuckDB's** for CSV / TSV / JSON,
**native** for Parquet / Avro / ORC / Arrow, and a custom **section-aware**
walk for XLSX / XLS / ODS (where one sheet is often N tables). When the
header looks fake (DuckDB fell back to `column00`, or the first row is a
number), a column-name proposer agent rewrites the names in place before
any downstream stage runs. Snapshot diffing detects added / removed / type-
changed columns plus position-and-type renames, with an LLM tiebreaker for
ambiguous cases that surfaces as `RENAMED_CANDIDATE` for human review.

---

## 1. The shape of the problem

"Just parse it" works for files that ML papers use as examples. Real-world
uploads break that assumption in five ways flyquery has to handle:

| Problem | Real example flyquery has seen |
| --- | --- |
| Merged-cell title banners | Orbis / BvD financial exports: rows 0-2 are merged-cell branding, the actual header is row 3 or 4. A naive `read_csv` returns a 1-column table whose values are the title strings. |
| Multi-section spreadsheets | A single Excel sheet contains a "Key figures" box, a "Financials per year" table, a "Contact" card, and a "Regulatory codes" footer — each with its own column count and section label. Treating the sheet as one flat table produces synthetic `columnNN` headers and mostly-NULL cells. |
| Encoded vs literal delimiters | A CSV with `"Smith, John"` in a single quoted cell, or a TSV that someone exported with semicolons. The sniffer has to look at the first 4-8 KB to decide. |
| Ambiguous JSON root | `data.json` could be a single object (one row), an array (N rows), or an object whose values are arrays (N tables). |
| Renames vs net-new columns | A column called `customer_id` disappears on re-upload and `cust_id` appears with the same type, position, and sample values. Did the data engineer rename it, or was the old column genuinely deleted and a new one added? |

Every stage below exists because of one of those five problems.

The pipeline as called by `IngestService.ingest_upload` (synchronous path):

```
1. receive      -> stages/receive.py
2. parse        -> stages/parse.py
3. reconcile    -> stages/reconcile.py
4. sample       -> stages/sample.py
5. profile      -> stages/profile.py
7. describe     -> stages/describe.py
9. embed        -> stages/embed.py
10. publish     -> stages/publish.py

Async-deferred (handled by IngestWorker, not on the critical path):
6. relations    -> stages/relations.py
8. pii_tag      -> stages/pii_tag.py
```

Stage numbers 6 and 8 are skipped in the synchronous path on purpose —
see `ingest_service.py:128-131`: "Stages 6 (relations), 8 (pii_tag)
intentionally deferred to the async worker; they're not on the critical
path for the first NL query against the table."

---

## 2. Format detection — magic bytes + extension

Source: `src/flyquery/core/services/ingestion/format_detect.py`

The detection function signature is:

```python
def detect_format(filename: str, head_bytes: bytes) -> tuple[str, str]:
    # returns (format, compression)
```

### 2.1 Precedence rule

**Extension always wins** when one of the recognised suffixes matches.
Magic bytes are a *fallback only*. The order is documented in the file
header: "Inspects the file extension first, then falls back to magic-byte
sniffing for files without a recognised extension."

This matters because:
- A Parquet file renamed to `.dat` will still be detected via the `PAR1`
  magic.
- A CSV file with a `.dat` extension will fail format detection (no
  text-format magic byte is checked — the `{` / `[` branch only catches
  obvious JSON).
- An XLSX with a `.xlsx.tmp` extension will likely be mis-detected as
  the `.tmp` extension is unknown, so we fall back to magic bytes —
  XLSX is a ZIP archive so we'll get `PK\x03\x04` and detect it as
  `xlsx` (which is what the operator usually wanted).

### 2.2 Compression unwrapping

Three compression wrappers are detected from the filename suffix only:

| Suffix | Compression code | Inner-format detection |
| --- | --- | --- |
| `.gz` | `gz` | strip 3 chars and re-detect from the inner name |
| `.bz2` | `bz2` | strip 4 chars and re-detect |
| `.zip` | `zip` | strip 4 chars and re-detect; zip must contain exactly one file |

The `.zip` case enforces **exactly one file** inside (`compression.py:55`):

```python
files = [n for n in zf.namelist() if not n.endswith("/")]
if len(files) != 1:
    raise ValueError(
        f"zip must contain exactly one file; got multiple files: {files}"
    )
```

Decompressed size is also bounded — `MAX_DECOMPRESSED_BYTES = 5 GB`
(`compression.py:15`). A zip-bomb is rejected mid-stream.

### 2.3 Per-format signatures

Magic-byte recognisers in priority order (`format_detect.py:56-70`):

```
PAR1            -> parquet
Obj\x01         -> avro
ORC             -> orc
ARROW1 / ARROW  -> arrow
PK\x03\x04      -> xlsx       (ZIP-based; .ods uses the same magic)
{ or [          -> json
```

ZIP-based formats (`xlsx`, `ods`, plain `.zip`) all start with
`PK\x03\x04`. The `.zip` extension is processed before reaching the
magic-byte fallback, so a bare `PK\x03\x04` magic is unambiguously
treated as `xlsx`. **This means an ODS file with a wrong extension
(no `.ods` suffix) will be mis-detected as `xlsx`** — operators should
rename the file or use the `.ods` suffix explicitly.

### 2.4 Ambiguity

If both the extension AND the magic byte recogniser miss, the function
raises:

```python
raise ValueError(f"could not detect format for {name!r}")
```

That bubbles up as a 400 from the upload controller. There is no
"try them all" mode — operators must rename the file or pass the
correct extension.

---

## 3. Per-format parsing strategies

The dispatch lives in `src/flyquery/core/services/ingestion/reader_factory.py:16`:

```
csv, tsv          -> CsvReader
xlsx, xls, ods    -> ExcelReader
json, jsonl       -> JsonReader
parquet           -> ParquetReader
avro              -> AvroReader
orc               -> OrcReader
arrow, feather    -> ArrowReader
```

Every reader implements the `FileReader` protocol from `reader.py:53`:

```python
async def enumerate_tables(source_path, rules) -> list[ProposedTable]
async def materialise(source_path, table, target_parquet_key, *,
                      workspace_locale, type_infer_sample_rows,
                      max_title_rows=3) -> MaterialiseResult
```

`enumerate_tables` is cheap (sample first 4 KB / read schema header);
`materialise` does the full conversion to Parquet.

### 3.1 CSV / TSV

Source: `src/flyquery/core/services/ingestion/readers/csv_reader.py`

flyquery delegates everything to DuckDB's `read_csv_auto`:

```sql
SELECT * FROM read_csv_auto(
    '{path}',
    sample_size={type_infer_sample_rows},   -- default 8192
    auto_detect=true,
    ignore_errors=false,
    dateformat='%d/%m/%Y'                   -- locale-dependent; see below
)
```

DuckDB auto-detects:
- **Delimiter**: tries `,`, `;`, `\t`, `|` over the first `sample_size` rows.
- **Header**: presence is inferred from whether the first row's values look
  type-distinct from the rest (a row of all-strings followed by numeric
  rows is a header).
- **Quoting**: `"` quote with `""` escape is the default.
- **Encoding**: UTF-8 with replacement on invalid bytes.

`enumerate_tables` only counts columns and estimates rows from the byte
size (`csv_reader.py:68`):

```python
est = max(1, byte_size // 80)  # ~80 bytes per row rough guess
```

The actual row count is computed during `materialise` after writing to
Parquet.

#### Locale-aware date hint

`_date_format_for_locale` (`csv_reader.py:122-143`) returns `%d/%m/%Y`
for the European locales `en-GB`, `fr`, `es`, `de`, `it`, `pt`, `nl`,
and `None` for everything else.

The rationale (verbatim from the source): DuckDB's default heuristic
prefers MM/DD interpretation when day ≤ 12, so `01/02/2026` becomes
Feb 1 in `en-US` and Jan 2 in `en-GB`. **The hint is only applied for
unambiguously-European locales** — adding it on `en-US` would force
`2026-01-15` (ISO) to widen from `DATE` to `TIMESTAMP` and degrade
schema quality.

### 3.2 XLSX / XLS / ODS

Source: `src/flyquery/core/services/ingestion/readers/excel_reader.py`

The Excel reader is the most ambitious code path in the entire codebase.
It uses `python-calamine` (fast Rust-backed reader) to load the workbook,
then runs a **section extraction** pass over each sheet's rows.

#### Section extraction (`_extract_sections`, lines 100-180)

A single sheet becomes N `ProposedTable`s when it looks like a dashboard.
The walk classifies every row as one of:

| Row pattern | Classification | Action |
| --- | --- | --- |
| 0 non-empty cells | empty | empty-run counter; ≥2 closes a section |
| 1 non-empty cell, type `str` | section label | becomes name of next section |
| 1 non-empty cell, not a string | data | continue collecting |
| ≥ 2 non-empty cells | section header | start a new section |

Two consecutive empty rows OR another single-cell-string row closes
the current section.

Column count is the **union of populated indices across the entire
section** (`excel_reader.py:163-167`), not just the header row. This
matters because merged-cell dashboards put real values at sparse
column indices like `[18, 32, 51, 70, 91]` and a header-only count
would underreport. The materialise step then *compacts* those columns
to consecutive positions so the resulting Parquet has dense schema.

#### Multi-sheet -> N tables

`_enumerate_sync` (`excel_reader.py:187-248`) emits one `ProposedTable`
per section. Naming:

- **Single-section sheet that covers the whole usable area**: table is
  named after the sheet (`Orders`, `Customers`). This is the classic
  "one tab per table" XLSX and stays backward-compatible with naive
  layouts.
- **Multi-section sheet**: each section's table is named
  `<sheet>__<section_label>`, with `_2`, `_3`, ... suffixes for
  collisions inside the same sheet.

The `sheet_or_json_path` field is encoded as
`<sheet_name>#section[<header_row>:<data_end>]` so the section's row
span is preserved across stages. `_parse_section_path` reverses this on
materialise.

#### Compaction and CSV round-trip

`_materialise_sync` (`excel_reader.py:263-395`) does:

1. Slice the section's row range.
2. **Compact populated columns** to consecutive positions (drop the empty
   columns between merged-cell gaps).
3. **Flatten embedded newlines** in cell strings to a single space (Excel
   cells can contain multi-line addresses; embedded `\n` breaks DuckDB's
   CSV dialect sniffer even inside double-quoted cells).
4. Write a temporary CSV (UTF-8, comma-delimited, `"` quoted).
5. Hand the temp CSV to DuckDB with **explicit dialect** (no sniffing):

```sql
read_csv_auto('{tmp}',
    sample_size={type_infer_sample_rows},
    auto_detect=true,
    ignore_errors=true,
    null_padding=true,
    delim=',', quote='"', escape='"',
    max_line_size=10000000)
```

The explicit `delim` / `quote` is critical for **single-column sections**
— DuckDB's dialect sniffer needs ≥2 columns to distinguish `,` from
`;` / `\t` / `|`, and a section with one column (e.g. an
"Industria y actividades" two-cell row) would otherwise fail. `max_line_size=10MB`
covers paragraph-length description cells that the default 2 MB cap
would reject.

#### Title-row heuristic (legacy backward-compat path)

When `sheet_or_json_path` is just a bare sheet name (no `#section[...]`
suffix), the reader falls back to a simpler heuristic (`excel_reader.py:288-296`):

```python
body_start = 0
for i in range(min(max_title_rows, len(rows))):
    non_empty = sum(1 for c in rows[i] if c not in (None, ""))
    if non_empty <= 1:
        body_start = i + 1
    else:
        break
section_rows = rows[body_start:]
```

This skips up to `max_title_rows` (default 3) of merged-cell title
banners before treating the rest of the sheet as a flat table.

### 3.3 JSON / JSONL

Source: `src/flyquery/core/services/ingestion/readers/json_reader.py`

#### Object-vs-array detection (`_is_jsonl`, lines 44-53)

JSONL detection has two strict triggers:
1. The file extension is `.jsonl` or `.ndjson`.
2. The first 1 KB contains multiple lines, all of which start with `{`
   when whitespace-trimmed.

Otherwise the file is treated as a single JSON document.

#### Root-type dispatch (`_enumerate_sync`, lines 56-106)

For a regular `.json` file:

| Root type | Behavior |
| --- | --- |
| `list` | One table, `n_rows_estimate = len(doc)`. |
| `dict` where any value is a `list` | One table per such key. Optional `rules.json_paths` allowlist filters which keys to extract. |
| `dict` with no list values | Falls through to "one 1-row table containing this object's fields". |
| anything else | Raises `ValueError`. |

For example, `data.json = {"users": [...], "orders": [...]}` becomes
two `ProposedTable`s with `sheet_or_json_path` set to `"users"` and
`"orders"` respectively.

#### Nested object flattening

flyquery does **not** flatten nested JSON objects — that's DuckDB's job
via `read_json_auto`. The materialise call is:

```sql
COPY (SELECT * FROM read_json_auto(
    '{src}', sample_size={type_infer_sample_rows}, format='auto'))
TO '{tgt}' (FORMAT PARQUET, COMPRESSION 'snappy')
```

DuckDB infers struct types for nested objects and array types for nested
arrays. The resulting Parquet columns can be `STRUCT(name VARCHAR, age INT)`
rather than two separate columns. Downstream stages handle struct types
as a single column whose `data_type` is the DuckDB struct representation.

### 3.4 Parquet / Avro / ORC / Arrow / Feather

These four formats already carry their own schema, so flyquery skips all
inference and reads the metadata directly.

| Format | Reader | Materialise strategy |
| --- | --- | --- |
| Parquet | `parquet_reader.py` | `shutil.copyfile` to the target key (zero conversion). |
| Avro | `avro_reader.py` | `fastavro` -> `pyarrow.Table.from_pylist` -> `pq.write_table` with snappy. Full file is materialised in memory — see "row count requires full scan" comment. |
| ORC | `orc_reader.py` | `pyarrow.orc.ORCFile.read()` -> `pq.write_table`. |
| Arrow / Feather | `arrow_reader.py` | `pyarrow.feather` for `.feather`; for `.arrow` tries `pyarrow.ipc.open_stream` first then falls back to `feather` (some `.arrow` files are Feather v2). |

All four use `pyarrow.Schema.field(i).type` as the column's `data_type`
string — so a Parquet column declared `int64` shows up as `"int64"` in
`flyquery_schema_objects.data_type`, while a CSV column inferred as
integer shows up as `"BIGINT"` (DuckDB's display name). This naming
asymmetry is a known wart; both retrieval and the relations heuristic
have type-group normalisers (`relations.py:_NUMERIC_GROUP`) so the
downstream code doesn't care.

---

## 4. Type inference (CSV + XLSX + JSON cases)

DuckDB does the actual inference. flyquery configures it via:

- `sample_size = settings.type_infer_sample_rows` (default **8192** —
  `config.py:68`)
- `auto_detect = true` always
- `dateformat = '%d/%m/%Y'` for European locales, otherwise unset

### 4.1 Sample-based inference

DuckDB reads the first `sample_size` rows, picks the **narrowest type
that fits all sampled values per column**, then casts subsequent rows
into that type. The precedence (DuckDB's, not flyquery's) is roughly:

```
BOOLEAN < INTEGER < BIGINT < HUGEINT < DOUBLE
         < DATE < TIMESTAMP < TIMESTAMP WITH TIME ZONE
         < VARCHAR
```

If a column has `"42"`, `"42.5"`, `"forty-two"` in sample rows, DuckDB
widens to `VARCHAR` (the only type that fits all three). With
`ignore_errors=false` (the default for CSV — `csv_reader.py:89`), a
cast failure on a non-sampled row aborts the read. The Excel path uses
`ignore_errors=true` because flatten-CSV intermediate files routinely
contain coerced strings that should silently become NULL.

### 4.2 Null tolerance

`NULL`, empty cells, the literal string `"NULL"` (case-insensitive when
`null_padding=true`), and Excel `None`/`""` cells all become Parquet
NULL. The `is_nullable` flag on `ColumnSchema` is read directly from
DuckDB's `DESCRIBE` output (`csv_reader.py:106`).

### 4.3 Timezone handling

DuckDB treats `2026-01-15T10:30:00Z` (with `Z` or `+00:00`) as
`TIMESTAMP WITH TIME ZONE` and `2026-01-15T10:30:00` (no offset) as
naive `TIMESTAMP`. The `profile.py:_TEMPORAL_TYPES` set recognises both
("timestamp", "timestamp with time zone", "timestamptz") so the profile
stage computes min/max for either.

### 4.4 Walkthrough — `"42"`, `"42.5"`, `"forty-two"`

Given a 3-row CSV:

```
amount
42
42.5
forty-two
```

With `type_infer_sample_rows=8192`, DuckDB reads all three (≤ sample
size), tries `INTEGER` (fails on `"42.5"`), tries `DOUBLE` (fails on
`"forty-two"`), and widens to `VARCHAR`. The resulting Parquet column
is `VARCHAR`, all three rows preserved as strings. No row is dropped.

If the file were 100,000 rows where `"forty-two"` only appeared at
row 50,000, DuckDB would still see it within the sample (because the
sample is the first N rows, but DuckDB also has a fallback "sniff
multiple chunks" mode — see DuckDB's own docs for the details). If the
sample missed it, the row read would either error (`ignore_errors=false`)
or silently NULL the cell (`ignore_errors=true`).

---

## 5. Column naming — LLM-assisted

Source: `src/flyquery/core/services/ingestion/stages/parse.py:135-217`
Prompt: `src/flyquery/resources/prompts/column_name_proposer.yaml`
Agent: `src/flyquery/core/agents/column_name_proposer_agent.py`

When DuckDB hands back columns named `column00`, `column01`, ..., or
when the first row was so weird that DuckDB picked actual data values
as headers (a number, an address string), flyquery rewrites them.

### 5.1 Trigger (`needs_proposal`)

`column_name_proposer_agent.py:109-135`. Three triggers in order:

1. **All-synthetic**: every name matches `^column\d+$` — DuckDB had no
   header band at all (classic dashboard-XLSX with merged title cells).
2. **All data-like**: every name looks like a data value (all numeric, all
   long-text, all date-ish).
3. **Majority data-like**: ≥ half the names look like data values, with
   a minimum of 1 — a section with 3 columns where 1 has a literal
   address as name is still rewritten.

Clean inputs (`id, name, email`) pass through with no LLM call — verified
by the test "Clean inputs pass through untouched".

### 5.2 Sample collection

If the trigger fires, `_read_parquet_sample` (`parse.py:107-132`) pulls
the first 5 rows from the just-materialised Parquet via DuckDB. The
agent sees:

- `section_label` — the section name from XLSX section extraction
  (e.g. "Activos", or the table name for non-XLSX).
- `current_names` — the literal `column00` / data-value names from
  DuckDB.
- `sample_values` — up to 5 values per column.

### 5.3 Agent contract

The prompt (`column_name_proposer.yaml`) demands:
- exactly `len(current_names)` proposed names, aligned 1:1
- lowercase ASCII, snake_case, ≤ 50 chars, starts with a letter, unique
- echo back already-good business names unchanged
- specific patterns for dates (`period_end_2024`), currencies
  (`currency`), addresses (`street_address`, `city`)
- fall back to `<section>_col_<n>` when truly uncertain

Output is forced into a Pydantic `ProposedColumnNames` model (the agent
uses pydantic-ai), so malformed JSON can't crash the pipeline.

### 5.4 Rewriting Parquet

`_rename_parquet_columns` (`parse.py:71-104`) rewrites the Parquet in
place using DuckDB:

```sql
COPY (SELECT col0 AS new0, col1 AS new1, ... FROM read_parquet('{src}'))
TO '{tmp_path}' (FORMAT PARQUET, COMPRESSION 'snappy')
```

The temp Parquet is then renamed over the original. Types and
nullability are preserved; only column names change.

### 5.5 Cost

The agent runs against `settings.describe_model` (default
`anthropic:claude-haiku-4-5`). One call per section that triggers the
proposer; payload is small (~5 rows × N columns). At haiku pricing
(~$0.80/M input + $4/M output) the average cost per section is on the
order of **$0.001-$0.002** — well under the typical describe cost.
There is **no batch budget** on the proposer call specifically (no
`column_name_proposer_budget` setting); it's bounded by the
`ingest_section_concurrency` semaphore (default 8 concurrent — see
`config.py:96`).

### 5.6 Graceful fallback

If `ANTHROPIC_API_KEY` is missing (`parse.py:166-172`), or the agent
returns a malformed list, or any exception fires, the column names
become `<section>_col_<n>` (`activos_col_0`, `activos_col_1`, ...).
These are at least scoped to the section so two different sections
don't collide in the search index.

---

## 6. Drift detection between snapshots

Source: `src/flyquery/core/services/ingestion/stages/reconcile.py`

Every materialised table becomes a new `flyquery_schema_snapshots`
row. The reconcile stage compares the new snapshot against the
**previous READY snapshot** for the same `table_id`.

### 6.1 What counts as drift

`reconcile.py:106-110`:

```python
added = [name for name in new_columns if name not in prev_columns]
removed = [name for name in prev_columns if name not in new_columns]
type_changed = [name for name in new_columns
                if name in prev_columns
                and new_columns[name] != prev_columns[name]]
```

Note: type comparison is **exact string equality** on the DuckDB type
display name. `INTEGER` -> `BIGINT` registers as a type change even
though both are integer. The grounding agent ignores this nuance —
it normalises via `relations._type_group`.

### 6.2 Rename detection (`_detect_renames`, lines 595-661)

Run only when both `removed` and `added` are non-empty.

1. **Group by type**: split removed and added columns by their declared
   data_type.
2. **Unambiguous match** — exactly one removed and one added column of
   the same type:
   - Auto-confirm as `RENAMED`. No LLM call.
3. **Ambiguous match** — N removed and M added of the same type (N ≥ 2
   or M ≥ 2):
   - Invoke the `RenameDetectionAgent` (`rename_detection.yaml`).
   - If the agent's top proposal has `confidence ≥ 0.8` (constant
     `_DEFAULT_AUTO_CONFIRM_THRESHOLD = 0.8`, `reconcile.py:27`), it
     becomes a `RENAMED` row.
   - Otherwise it becomes a `RENAMED_CANDIDATE` row — human review
     required.

### 6.3 `RENAMED_CANDIDATE` vs `RENAMED`

The state is separate because **acting on it is irreversible**. A
confirmed `RENAMED` flips the schema_objects' annotation transplant —
human-set descriptions, synonyms, business owner, governance JSON
flow from the old name to the new name. A wrong rename would orphan
the annotations.

`RENAMED_CANDIDATE` is a proposal: the change row sits in
`flyquery_schema_changes` with `after_json.candidates = [list of
candidate new names]`. The annotation transplant is **not** applied
until an operator confirms.

### 6.4 Drift policy

The dataset-level field is `flyquery_datasets.drift_policy`
(`entities/dataset.py:32`). The interface enum
(`interfaces/datasets.py:17, 26, 38`) declares only two values:

```python
drift_policy: Literal["AUTO", "MANUAL"] = "AUTO"
```

There is **no STRICT mode in the code today**. The original spec
mentions one, and other docs reference it, but the current codebase
only supports:

| Policy | Behavior |
| --- | --- |
| `AUTO` | Confirmed renames auto-apply; candidate renames stay as `RENAMED_CANDIDATE`. The upload always completes. |
| `MANUAL` | Same diff is recorded but no auto-confirmation flows through. (The actual gating logic for MANUAL is at the controller layer — see `schema_changes_controller.py`.) |

A future STRICT mode would reject the upload when drift is detected;
operators relying on it should treat that as v1+ scope.

### 6.5 Operator confirmation endpoint

```
POST /api/v1/schema-changes/{change_id}:confirm
```

`web/controllers/schema_changes_controller.py:37-76`. It:
- Validates the change is in state `RENAMED_CANDIDATE`.
- Sets `change = 'RENAMED'`, `approved_by = actor`, `approved_at = now()`.
- Updates `last_changed_at` on the corresponding `flyquery_schema_objects`
  column row.

There is **no batch confirm endpoint** today — operators confirm one
change at a time.

### 6.6 Removed columns

`_mark_removed_columns_inactive` (`reconcile.py:373-405`) flips
`is_active = false` on the previous snapshot's column row but **does
not delete the row**. This preserves historical pinning: a query saved
against an old snapshot can still resolve the column name to its
historical type and description.

---

## 7. PII tagging

Source: `src/flyquery/core/services/pii/`, stages: `sample.py` + `pii_tag.py`

### 7.1 Default scanner — regex

`adapters/regex_scanner.py`. Five patterns, applied in this order:

| Tag | Pattern |
| --- | --- |
| `EMAIL` | `\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b` (RFC 5322 simplified) |
| `SSN` | `\b(?!000\|666\|9\d\d)\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b` (excludes US invalid prefixes) |
| `CREDIT_CARD` | `\b(?:\d{4}[ \-]?){3}\d{4}\b` — Luhn-friendly groupings, **no checksum validation** |
| `PHONE` | `(?<!\d)(?:\+?\d{1,3}[\s.\-]?)?(?:\(\d{2,4}\)\|\d{2,4})[\s.\-]?\d{3,4}[\s.\-]?\d{3,4}(?!\d)` (≥7 digits) |
| `IP_ADDRESS` | Standard IPv4 dotted-quad with octet bounds |

Plus column-name keyword hints (`_NAME_HINTS`): `email` / `mail`,
`ssn` / `social_security`, `phone` / `mobile`, `credit_card` /
`card_number`, `ip` / `ip_address`. A hit on the column name alone
tags the column even before sample scanning.

### 7.2 Optional Presidio scanner

`adapters/presidio_scanner.py` (66 lines). Wraps Microsoft Presidio when
the `[presidio]` extra is installed. Provides ~50+ entity types
including names, addresses, dates of birth, medical record numbers, and
language-specific identifiers.

Selected via `FLYQUERY_PII_SCANNER=presidio`. If the import fails (extra
not installed), the factory raises ImportError loudly rather than
silently falling back — this is intentional, `pii/factory.py:36`.

### 7.3 49-label semantic type taxonomy

PII tagging is **separate** from semantic type classification. Semantic
types (`describe.yaml`) classify what a column represents (amount,
percentage, country_code, date), while PII tags flag privacy-sensitive
contents (EMAIL, SSN, PHONE). Some overlap exists (`email` semantic type
implies `EMAIL` PII tag) but the codepaths are independent.

See [`docs/semantic-types.md`](semantic-types.md) for the full taxonomy.

### 7.4 PII policy on samples

`settings.pii_policy_samples` (default `"redact"`) — `pii_tag.py:38`:

| Policy | Action |
| --- | --- |
| `warn` | Tag `pii_tag` + log; samples stay visible. |
| `redact` | Tag `pii_tag` + `sample_values_json = '[]'::jsonb`. |
| `reject` | Tag `pii_tag` + `is_active = false`. Column hidden from grounding/retrieval; human must review. |

There is also an **inline gate at sample time** (`sample.py:71-77`):
every value sampled is passed through `scan_single` BEFORE persistence,
and PII-tainted values are silently dropped. If **all** sampled values
are tainted, no sample row is persisted at all. This is a defense-in-
depth measure — even if the column-level policy is `warn`, you can't
accidentally store a sample value that's PII.

### 7.5 HUMAN override

`reconcile.py:332-370` (`_load_human_annotations`) carries forward
`pii_source = 'HUMAN'` from the previous snapshot. If an operator
manually tagged a column on a previous snapshot, the new snapshot
inherits that tag — agent passes do **not** overwrite human-set values.

The same protection covers `description_source = 'HUMAN'` and
`business_owner IS NOT NULL`.

---

## 8. Description generation

Source: `src/flyquery/core/services/ingestion/stages/describe.py`
Prompt: `src/flyquery/resources/prompts/describe.yaml`

### 8.1 Trigger

`_load_undescribed_columns` (`describe.py:157-214`) picks active columns
where **both** `description IS NULL` AND `description_source IS NULL`.
A human-set description (`description_source = 'HUMAN'`) is skipped
forever; the agent never overwrites it.

### 8.2 What the agent sees

`_build_prompt` (`describe.py:138-154`) constructs:

```json
{
  "qualified_name": "sales_dataset.orders.total_amount",
  "data_type": "DOUBLE",
  "samples": ["1234.56", "987.00", "1500.00", "23.10", "45000.00"],
  "table_context": ["id", "customer_id", "order_date", "currency", ...]
}
```

- `samples` is capped at 5 values (already PII-filtered by stage 4).
- `table_context` is the list of sibling columns under the same parent
  TABLE, capped at 20 names.

### 8.3 What the agent returns

For each column:

| Field | Purpose |
| --- | --- |
| `description` | 1-2 sentence business description (≠ "the column name in English"). |
| `synonyms` | 3-8 alternative business names the analyst might use. |
| `semantic_type` | One of the 49 taxonomy labels (see `describe.yaml`). |

Storage:
- `description`, `synonyms_json` -> direct columns.
- `semantic_type` -> stored inside `governance_json` as
  `{"semantic_type": "<label>"}` (no schema migration was required;
  `describe.py:243-251`).

### 8.4 Batching and budget

- Batch size: `settings.describe_batch = 20` columns per LLM call.
- Per-run budget: `settings.describe_budget_cents_per_run = 200` cents
  (i.e. $2.00).
- Cost accounting uses haiku pricing: $0.80/M input + $4/M output
  tokens (`describe.py:29-30`).

When the budget is exhausted, remaining columns are flagged as
**deferred**. They'll be picked up by the `DESCRIBE_PASS` background
job — `IngestWorker._run_describe_pass` (`workers.py:568+`) — on its
next scan.

### 8.5 Source precedence

`description_source` ∈ {`HUMAN`, `AGENT`}.

- `HUMAN` always wins. Agent passes filter out `description_source = 'HUMAN'`.
- `AGENT` is overwritten by subsequent agent passes only if the prompt
  changes (currently no prompt-version tracking — see §9.4).

---

## 9. Embedding generation

Source: `src/flyquery/core/services/ingestion/stages/embed.py`,
`src/flyquery/core/services/retrieval/embedder.py`

### 9.1 What gets embedded

`_build_embed_text` (`embed.py:128-142`) builds:

```
<qualified_name>: <data_type>
<description>
Synonyms: <comma-joined list>
```

Every `flyquery_schema_objects` row in the snapshot (both `TABLE` and
`COLUMN` kinds) gets one embedding. The text combines:
- The qualified name (`sales.orders.total_amount`).
- The data type, appended after a colon.
- The agent-generated description (if any).
- The synonyms list (if any).

### 9.2 Provider matrix

`config.py:114-116` — `embedding_provider` is a `Literal` over:

```
ollama, openai, cohere, voyage, azure, google, mistral, bedrock, null
```

Defaults: `ollama` + `nomic-embed-text` (768-d native). This lets
`docker compose up` work end-to-end without paid API keys.

| Provider | Notes |
| --- | --- |
| `ollama` | Local embeddings; requires Ollama running on `embedding_base_url`. |
| `openai` | `text-embedding-3-{small, large}` |
| `cohere` | `embed-english-v3.0` (1024-d) |
| `voyage` | `voyage-3`, `voyage-large-2` |
| `azure` | Azure OpenAI deployments |
| `google` | Vertex AI text-embedding |
| `mistral` | `mistral-embed` |
| `bedrock` | AWS Titan / Cohere on Bedrock |
| `null` | No vectors written; retrieval uses BM25 over `content_tsv` only. |

If a provider's API key / endpoint is unreachable, the factory
(`embedder.py:206-216`) **downgrades to `NullEmbedder`** rather than
failing — ingestion completes and BM25 retrieval still works.

### 9.3 Dimension padding

The `flyquery_schema_objects.embedding` column is fixed at
`vector(settings.embedding_dimensions)` — default **1536**.

Native dimensions per provider:
- `nomic-embed-text`: 768
- OpenAI `text-embedding-3-small`: 1536 (native — no padding)
- Cohere v3: 1024
- Voyage: 1536

`FireflyEmbedder._pad` (`embedder.py:146-158`) zero-pads to 1536 when
the native dim is smaller, and **truncates** when larger.

> Cosine similarity is preserved under zero-padding because zero
> coordinates contribute zero to both the dot product and the L2 norms.
> Rankings stay stable. Truncation is genuine information loss but is
> rare — only providers whose native dim exceeds 1536 are affected.

### 9.4 Re-embed triggers

`run_embed` is called per-snapshot at ingestion time. The system
**does not** re-embed columns when:
- The describe prompt changes.
- The embedding provider changes.
- The embedding model is upgraded.

There is no `EMBED_PASS` job in `workers.py` — this is documented v1+
scope. The workaround today is to trigger a `REPARSE` job (which
re-runs stages 1-3 + 9-10) for the affected table.

### 9.5 BM25 fallback

Whether or not embeddings succeed, every object gets a
`content_tsv` PostgreSQL tsvector built from the embed text
(`embed.py:158-195`):

```sql
content_tsv = to_tsvector('english', :tsv_input)
```

Input is capped at 4096 chars (PostgreSQL tsvector limit guard).
Retrieval can hit this even when the vector column is NULL.

---

## 10. Worked example — `Q1 dashboard.xlsx`

Operator uploads a 4.2 MB file `Q1 dashboard.xlsx` containing 6 sheets:

| Sheet | Layout |
| --- | --- |
| `Cover` | Logo image + 2 merged-cell text rows. No tabular data. |
| `KPIs` | Single section with 4 columns, 3 rows. |
| `Sales` | Two sections: "By region" (5 cols × 8 rows), "By product" (4 cols × 15 rows). |
| `Costs` | One section with 6 columns, 25 rows. Merged-cell title in row 0. |
| `Headcount` | One section, but the first row is `5302354.32` (looks like a number — Excel exported with no header). 7 columns, 12 rows. |
| `Notes` | Free-text paragraphs — no tabular structure. |

### 10.1 Stage-by-stage walkthrough

| Stage | What happens | Wall-clock (est.) |
| --- | --- | --- |
| 1. receive | SHA-256 hash computed. Cap check passes (4.2 MB < `max_file_mb=2048`). `detect_format("Q1 dashboard.xlsx", head_bytes) -> ("xlsx", "none")`. `flyquery_files` row inserted with `status='RECEIVED'`. | ~50 ms |
| 2. parse | `python_calamine` opens the workbook. `_extract_sections` runs once per sheet. `Cover` and `Notes` yield 0 sections each — skipped. `Sales` yields 2 sections. Net: **5 `ProposedTable`s** (KPIs, Sales__By_region, Sales__By_product, Costs, Headcount). Each materialised to a temp CSV, then DuckDB writes Parquet. `Headcount` triggers `needs_proposal=True` (all column names are numeric data values) — the column-name proposer agent rewrites the 7 columns to e.g. `[employee_id, name, department, salary, hire_date, manager_id, status]`. `Costs` has its merged title row stripped by the `max_title_rows=3` heuristic OR by the section extractor recognising row 0 as a 1-cell label. | 600-900 ms (LLM call for Headcount adds ~700 ms) |
| 3. reconcile | First upload — `prev_snapshot = None` for all 5 tables. No diff written. For each table, one `flyquery_schema_snapshots` row + one `TABLE` schema_object + N `COLUMN` schema_objects. Status `PARTIAL`. | ~150 ms × 5 = 750 ms |
| 4. sample | For each column without `pii_tag`, read up to `sample_n=8` non-null values from the Parquet. Each value passed through `RegexPiiScanner.scan_single`. Clean values persisted to `sample_values_json`. | ~50 ms × 5 = 250 ms |
| 5. profile | Per column: count, null_count, approx_count_distinct. For numeric/temporal: min, max. For low-cardinality (distinct ≤ 100): top 5. Skipped if any single table exceeds `profile_row_threshold=10M` rows (none do here). | ~30 ms × 5 = 150 ms |
| 7. describe | Across 5 tables, ~30 columns total. Batched at 20/call, so **2 LLM calls**. Each column gets a description, 3-8 synonyms, and a semantic_type. Budget consumed: ~$0.05. | 2-4 seconds (haiku is fast) |
| 9. embed | All ~35 schema_objects (5 TABLE + 30 COLUMN) embedded in a single batch call. With Ollama + `nomic-embed-text`, 768-d vectors zero-padded to 1536. `content_tsv` written for every row. | 500-800 ms |
| 10. publish | Atomic flip: each snapshot `status='READY'` + `flyquery_tables.current_snapshot_id` updated. `flyquery.schema.updated` EDA event published. | ~100 ms × 5 = 500 ms |

**Total wall-clock estimate**: ~6-9 seconds for the synchronous path.

Async-deferred:
- Stage 6 (relations) runs in the worker. Will discover that `Sales__By_region.region` and `Sales__By_product.region` share a name + type + look like a heuristic join.
- Stage 8 (pii_tag) runs in the worker. May tag `Headcount.salary` (no PII match) and `Headcount.employee_id` (no PII match unless the values look like SSNs).

### 10.2 Resulting database state

```
flyquery_files:                  1 row  (status=RECEIVED)
flyquery_tables:                 5 rows (KPIs, Sales__By_region,
                                         Sales__By_product, Costs,
                                         Headcount)
flyquery_schema_snapshots:       5 rows (status=READY)
flyquery_schema_objects:         5 TABLE + ~30 COLUMN = ~35 rows
flyquery_schema_changes:         0 rows (first upload, no diff)
flyquery_relations:              ≥1 row from heuristic 6a
                                 (after async worker runs)
```

If the operator re-uploads the same file a week later with `region`
renamed to `region_name` in `Sales__By_region`:

- Stage 3 detects `region` in `removed`, `region_name` in `added`, same
  data_type (`VARCHAR`).
- Unambiguous match → auto-confirmed `RENAMED`.
- Annotation transplant: any HUMAN description on `region` flows to
  `region_name`.
- `flyquery_schema_changes` gets one `RENAMED` row.

If they also renamed `Costs.amount` to `Costs.cost_amount` AND added
`Costs.amount_eur` of the same VARCHAR type:

- Two removed columns and two added columns with overlapping types.
- Ambiguous → `RenameDetectionAgent` invoked.
- If the agent returns `(amount, cost_amount, confidence=0.92)` →
  auto-confirmed `RENAMED`; the leftover `amount_eur` is treated as
  `ADDED`.
- If the agent returns `(amount, cost_amount, confidence=0.65)` →
  becomes `RENAMED_CANDIDATE`. Operator must POST to
  `/api/v1/schema-changes/{change_id}:confirm`.

---

## 11. Troubleshooting

### 11.1 "My CSV got the wrong delimiter"

DuckDB's sniffer trusts the first 4 KB. If your CSV's first 4 KB contain
non-representative content (e.g. a comment header + a single sparse
row), the sniffer guesses wrong.

**Workaround**: there is no public delimiter override on the upload API
today. The only knob is `type_infer_sample_rows` (`config.py:68`,
default **8192**) which controls how many rows DuckDB sees, not the
delimiter choice. If you control the export, prefer TSV (which always
uses tab) or a Parquet file (no inference at all).

### 11.2 "My XLSX title rows weren't skipped"

The section extractor *should* handle this — a single-cell-string row
at the top of the sheet becomes a section label, not a header. If you
see the title text appearing in column values:

1. Check that the title cell is actually a single string and not a
   merged range that python-calamine returns as multiple non-empty
   cells.
2. The legacy backward-compat path (sheet with one section covering the
   whole sheet) uses `max_title_rows` (default **3**, `config.py:67`).
   If your title banner is more than 3 rows tall, bump this knob.
3. Excel "Group Boxes" and "Comments" sometimes show as cells. They're
   not — they're metadata. python-calamine ignores them.

### 11.3 "My dates parsed as strings"

Two likely causes:

1. The column has mixed formats (`2026-01-15` and `15/01/2026` in the
   same column). DuckDB widens to VARCHAR. Fix at the source.
2. Your locale is `en-US` (the default) but the dates are `DD/MM/YYYY`.
   The `dateformat` hint isn't applied (`csv_reader.py:141-143` —
   only European locales get the hint). Set the workspace's
   `default_locale` to `en-GB` / `fr` / `es` / `de` / `it` / `pt` /
   `nl` and re-upload. The locale flows through `IngestService` and
   onto `reader.materialise(workspace_locale=...)`.

### 11.4 "Rename detection caught a false positive"

It happens when two unrelated columns share a data_type and the LLM
confidence overshoots 0.8.

Recovery path:
1. Set the dataset's `drift_policy = 'MANUAL'`. Future uploads will
   record diffs but not auto-confirm renames.
2. To roll back the false positive: re-upload the file with the rename
   intent inverted, or manually update the `flyquery_schema_changes`
   row to `change = 'RENAMED'` with an empty annotation transplant
   (requires direct DB access today — there's no REST endpoint for
   un-renames).
3. The `_DEFAULT_AUTO_CONFIRM_THRESHOLD = 0.8` constant is not
   currently exposed as a setting (`reconcile.py:27`). Tightening it
   to 0.9 requires a code change.

---

## 12. Reference

### 12.1 Related docs

- [`docs/file-formats.md`](file-formats.md) — per-format quirks and the
  upload payload reference.
- [`docs/semantic-types.md`](semantic-types.md) — the full 49-label
  taxonomy used by `DescribeAgent`.
- [`docs/prompts.md`](prompts.md) — every prompt template flyquery
  ships, with versioning rules.
- [`docs/ingestion.md`](ingestion.md) — top-level ingestion guide
  including the EDA flow, idempotency contract, and partial-failure
  recovery.
- [`docs/pii.md`](pii.md) — PII scanner internals + the configuration
  matrix.
- [`docs/embeddings.md`](embeddings.md) — embedding provider details
  and the BM25-fallback retrieval path.

### 12.2 Tunable knobs (from `flyquery.config.FlyquerySettings`)

| Setting | Default | Effect on schema detection |
| --- | --- | --- |
| `max_file_mb` | 2048 | Per-file upload cap (HTTP 413 above this). |
| `max_workspace_gb` | 200 | Workspace-wide storage cap. |
| `type_infer_sample_rows` | 8192 | Rows DuckDB inspects for CSV / JSON / XLSX-as-CSV type inference. |
| `max_title_rows` | 3 | Title-row banner skip in legacy XLSX path. |
| `default_locale` | `en-US` | Determines `dateformat` hint for CSV. European locales get `%d/%m/%Y`. |
| `sample_n` | 8 | Sample values pulled per column in stage 4. |
| `profile_row_threshold` | 10_000_000 | Tables larger than this skip stage 5 entirely. |
| `describe_batch` | 20 | Columns per describe-agent LLM call. |
| `describe_budget_cents_per_run` | 200 | Per-snapshot describe budget (cents). Excess deferred to DESCRIBE_PASS. |
| `relation_proposer_enabled` | true | Toggles stage 6b (LLM relation proposer). |
| `relation_heuristic_min_confidence` | 0.5 | Minimum heuristic-stage confidence for relation insert. |
| `relation_proposer_max_per_pair` | 3 | Cap on agent proposals per table pair. |
| `pii_scanner` | `regex` | `regex` / `presidio` / `disabled`. |
| `pii_policy_samples` | `redact` | `warn` / `redact` / `reject`. |
| `embedding_provider` | `ollama` | Selects embedding backend. `null` -> BM25-only retrieval. |
| `embedding_model` | `nomic-embed-text` | Provider-specific model name. |
| `embedding_dimensions` | 1536 | Fixed column width of `vector(N)`. Smaller native vectors are zero-padded. |
| `embedding_native_dim` | 768 | Native dim of the selected model. |
| `ingest_section_concurrency` | 8 | Parallel XLSX sections (each section can fire 1 describe + 1 column-naming LLM call). |
| `ingest_worker_concurrency` | 4 | Async ingest worker fan-out for deferred jobs. |

### 12.3 Source-of-truth files

| Concern | Path |
| --- | --- |
| Format detect | `src/flyquery/core/services/ingestion/format_detect.py` |
| Compression | `src/flyquery/core/services/ingestion/compression.py` |
| Reader dispatch | `src/flyquery/core/services/ingestion/reader_factory.py` |
| Per-format readers | `src/flyquery/core/services/ingestion/readers/*.py` |
| Pipeline orchestration | `src/flyquery/core/services/ingestion/ingest_service.py` |
| Stages | `src/flyquery/core/services/ingestion/stages/*.py` |
| Async worker (DESCRIBE_PASS / RELATION_PASS / REPARSE) | `src/flyquery/core/services/ingestion/workers.py` |
| Settings | `src/flyquery/config.py` |
| Prompts | `src/flyquery/resources/prompts/*.yaml` |
| Embedder | `src/flyquery/core/services/retrieval/embedder.py` |
| PII | `src/flyquery/core/services/pii/` |
| Schema-change confirm endpoint | `src/flyquery/web/controllers/schema_changes_controller.py` |
| Derived tables (SELECT-as-table) | `src/flyquery/core/services/derived/derived_table_service.py` |
