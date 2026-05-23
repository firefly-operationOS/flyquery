# flyquery — File Formats

## Table of Contents

1. [Supported formats at a glance](#1-supported-formats-at-a-glance)
2. [Compression variants](#2-compression-variants)
3. [Format reader matrix](#3-format-reader-matrix)
   - [CSV / TSV](#csv--tsv)
   - [XLSX / XLS / ODS](#xlsx--xls--ods)
   - [JSON / JSONL](#json--jsonl)
   - [Parquet](#parquet)
   - [Avro](#avro)
   - [ORC](#orc)
   - [Arrow / Feather](#arrow--feather)
4. [Multi-table extraction rules](#4-multi-table-extraction-rules)
5. [Format detection](#5-format-detection)
6. [Edge cases and limits](#6-edge-cases-and-limits)

---

## 1. Supported formats at a glance

| Format family | Extensions | Multi-table? | Reader class |
|---------------|-----------|--------------|-------------|
| Delimited text | `.csv`, `.tsv` | No | `CsvReader` |
| Excel / ODS | `.xlsx`, `.xls`, `.ods` | Yes (one per sheet) | `ExcelReader` |
| JSON | `.json`, `.ndjson` | Sometimes (top-level object keys) | `JsonReader` |
| JSON Lines | `.jsonl`, `.ndjson` | No | `JsonReader` |
| Parquet | `.parquet`, `.pq` | No | `ParquetReader` |
| Avro | `.avro` | No | `AvroReader` |
| ORC | `.orc` | No | `OrcReader` |
| Arrow IPC / Feather | `.arrow`, `.feather` | No | `ArrowReader` |

All formats support `.gz`, `.zip`, and `.bz2` compression transparently
(see [§2](#2-compression-variants)).

File size limit: `FLYQUERY_MAX_FILE_MB` (default 2048 MiB = 2 GiB).

---

## 2. Compression variants

Compressed files are detected from both magic bytes and extension. The
decompression layer opens a temp buffer, decompresses, and delegates to the
inner reader.

| Extension | Algorithm | Notes |
|-----------|-----------|-------|
| `.gz` | gzip | Single-stream; `gzip.open` pass-through |
| `.bz2` | bzip2 | Single-stream; `bz2.open` pass-through |
| `.zip` | zip | Multi-entry ZIPs are rejected if they contain more than one file or if the decompressed size exceeds the file size cap |

Compression is stored in `flyquery_files.compression`
(`none` | `gz` | `zip` | `bz2`). The original compressed blob is retained
in object storage under `files/{file_id}.{ext}.{compression}`.

A double-extension like `orders.csv.gz` is fully supported: flyquery first
decompresses the gzip, then applies the CSV reader.

---

## 3. Format reader matrix

### CSV / TSV

**Extensions**: `.csv`, `.tsv`

**Reader**: `CsvReader` — `core/services/ingestion/readers/csv_reader.py`

**Detection**:
- Magic bytes: none (text file); primarily extension-based.
- For `.csv`, delimiter is sniffed from the first 8 KiB using Python's
  `csv.Sniffer`. Common delimiters tried: `,`, `;`, `\t`, `|`.
- For `.tsv`, delimiter is forced to `\t`.

**Encoding detection**:
- `charset-normalizer` (preferred) or `chardet` reads the first 64 KiB to
  detect the charset.
- Common detections: UTF-8, UTF-16, latin-1, Windows-1252, Shift-JIS.
- On detection failure, defaults to UTF-8 with `errors=replace`.

**Materialisation**:
- DuckDB `read_csv_auto(sample_size=FLYQUERY_TYPE_INFER_SAMPLE_ROWS,
  auto_detect=true, encoding=<detected>)` produces the Parquet output.
- Workspace locale controls DuckDB's date format parser
  (`FLYQUERY_DEFAULT_LOCALE`).
- Always produces **one table**.

**Type inference**:
- DuckDB's `auto_detect=true` infers VARCHAR, BIGINT, DOUBLE, DATE, TIMESTAMP,
  BOOLEAN.
- After `type_infer_sample_rows`, remaining rows are cast; mismatches become
  VARCHAR.

**Edge cases**:
- **BOM** — UTF-8 BOM (`\xef\xbb\xbf`) is stripped before parsing.
- **Quoted newlines** — DuckDB handles RFC 4180 multiline quoted fields.
- **Mixed quoting** — both `"` and `'` quoting styles in the same file;
  DuckDB sniffs the predominant style.
- **Ragged rows** — rows with fewer columns than the header are padded with
  NULL; rows with more columns are rejected with a `WARN` event.
- **Empty file** — produces a table with zero rows and zero columns; the job
  succeeds with a warning.

---

### XLSX / XLS / ODS

**Extensions**: `.xlsx`, `.xls`, `.ods`

**Reader**: `ExcelReader` — `core/services/ingestion/readers/excel_reader.py`

**Library**: `python-calamine` (preferred for performance; falls back to
`openpyxl` for `.xlsx`-specific features).

**Multi-table extraction**:
- Each sheet → one `flyquery_tables` row.
- Sheet names are sanitised (non-alphanumeric characters replaced with `_`;
  leading digits prefixed with `t_`).
- `table_extraction_rules_json.sheet_allowlist` limits extraction to named
  sheets only.

**Title-row skipping**:
- Sheets often have a company logo or title merged across the top rows.
- flyquery skips up to `FLYQUERY_MAX_TITLE_ROWS` (default 3) rows before the
  first row that resembles a header (short strings, no merged cells).
- `table_extraction_rules_json.header_skip_rows` overrides this.

**Type inference**:
- `python-calamine` preserves native Excel cell types (dates, numbers,
  booleans). These are written directly to the Parquet target via DuckDB.

**Edge cases**:
- **Merged cells** — horizontal merges in data rows have the value in the
  first cell and NULL in subsequent cells. Vertical merges are forward-filled
  (the value propagates down until the next non-empty cell).
- **Hidden sheets** — included unless excluded by `sheet_allowlist`.
- **Empty sheets** — produce a table with zero rows; the job succeeds.
- **ODS formula cells** — evaluated to their last cached value.
- **Very wide sheets** (>1000 columns) — materialised as-is; embedding
  budget cap applies (`ingest_policy_json.include_columns` recommended).

---

### JSON / JSONL

**Extensions**: `.json`, `.jsonl`, `.ndjson`

**Reader**: `JsonReader` — `core/services/ingestion/readers/json_reader.py`

**DuckDB functions**:
- `read_json_auto` for both JSON and JSONL.
- JSONL is treated as one table regardless of content.

**Multi-table extraction (JSON only)**:
- **Top-level array** `[...]` → one table.
- **Top-level object with array-valued keys**:
  ```json
  {"orders": [...], "customers": [...]}
  ```
  → two tables (`orders`, `customers`).
- **Nested objects** that are not arrays → a single table with complex-type
  columns (DuckDB STRUCT/MAP). These remain queryable but are not
  further exploded. Use `/tables:explode` (v1+) for nested flattening.
- `table_extraction_rules_json.json_path_spec` constrains which top-level
  keys to extract.

**Type inference**:
- DuckDB `auto_detect=true` infers types from the JSON values.
- Heterogeneous arrays (e.g., mixed numbers and strings) collapse to VARCHAR.

**Edge cases**:
- **Large nested arrays** — columns containing embedded JSON arrays are stored
  as DuckDB `JSON` type (text blob).
- **Duplicate keys** — JSON spec does not forbid them; DuckDB takes the last
  value.
- **Date strings** — not auto-converted; left as VARCHAR unless workspace
  locale explicitly casts them.

---

### Parquet

**Extensions**: `.parquet`, `.pq`

**Reader**: `ParquetReader` — `core/services/ingestion/readers/parquet_reader.py`

**Behaviour**: Pass-through. flyquery reads the schema metadata via PyArrow,
then writes the file through to the snapshot Parquet key without re-encoding.
Schema types are preserved exactly.

**No type inference**: schema is authoritative. Column types come from the
Parquet schema, not from sampling.

**Multi-table**: No. One file → one table.

**Edge cases**:
- **Row group count** — no limit; DuckDB attaches the file and queries across
  all row groups transparently.
- **Schema evolution across row groups** — DuckDB handles schema evolution
  within a single Parquet file; incompatible column type changes raise a parse
  error.
- **Dictionary encoding** — transparent to flyquery.
- **Nested columns (repeated groups)** — stored as DuckDB MAP/STRUCT types;
  not flattened.

---

### Avro

**Extensions**: `.avro`

**Reader**: `AvroReader` — `core/services/ingestion/readers/avro_reader.py`

**Behaviour**: Avro is read via DuckDB's `read_avro` function (if available in
the DuckDB build) or via PyArrow's Avro reader. The result is materialised to
Parquet.

**Schema source**: Avro's embedded schema JSON is used directly. Union types
that include `null` become nullable columns.

**Edge cases**:
- **Avro unions** (multiple non-null types) — collapsed to VARCHAR.
- **Avro maps** — stored as DuckDB MAP type.
- **Schema registry** — not supported; schema must be embedded in the file.

---

### ORC

**Extensions**: `.orc`

**Reader**: `OrcReader` — `core/services/ingestion/readers/orc_reader.py`

**Behaviour**: ORC is read via DuckDB's `read_orc` or PyArrow's `orc.read_table`.
Result is materialised to Parquet.

**Edge cases**:
- **Bloom filters and column statistics** — read by DuckDB for predicate
  pushdown during profiling queries.
- **Stripe split** — transparent; DuckDB reads all stripes.
- **ORC ACID tables** (Hive transactional) — the delta files are not merged;
  only the base file is ingested.

---

### Arrow / Feather

**Extensions**: `.arrow`, `.feather`

**Reader**: `ArrowReader` — `core/services/ingestion/readers/arrow_reader.py`

**Behaviour**: PyArrow IPC stream (`ipc.open_file`) or Feather V2
(`feather.read_table`). The in-memory Arrow table is written to Parquet.

**Edge cases**:
- **Feather V1** (`.feather` from pyarrow < 0.17) — not supported; upgrade the
  export tool or convert offline.
- **Large binary columns** — stored as DuckDB BLOB; not embedded or sampled.
- **Dictionary-encoded columns** — decoded to their value type before Parquet
  materialisation.

---

## 4. Multi-table extraction rules

The `table_extraction_rules_json` field on a `flyquery_files` row controls
which logical tables are extracted:

```json
{
  "sheet_allowlist": ["Sheet1", "Sheet3"],
  "json_path_spec": ["orders", "customers"],
  "header_skip_rows": 2
}
```

| Field | Applies to | Behaviour |
|-------|-----------|-----------|
| `sheet_allowlist` | XLSX/XLS/ODS | Only extract the listed sheets. Sheets not in the list are silently skipped. |
| `json_path_spec` | JSON | Only extract the listed top-level keys. Keys not in the list are skipped. |
| `header_skip_rows` | CSV/TSV, XLSX/XLS/ODS | Skip this many rows before treating the next row as the header. Overrides auto-detection. |

If `table_extraction_rules_json` is absent or `{}`, auto-detection applies
for all formats.

---

## 5. Format detection

flyquery uses a two-step detection:

1. **Magic bytes** — first 16 bytes of the file are checked against known
   signatures:
   - Parquet: `50 41 52 31` (`PAR1`)
   - ORC: `4F 52 43` (`ORC`)
   - Avro: `4F 62 6A 01` (`Obj\x01`)
   - Arrow IPC: `41 52 52 4F 57 31 00 00` (`ARROW1\0\0`)
   - Feather V2: `46 45 41 31` (`FEA1`)
   - XLSX: `50 4B 03 04` (ZIP container — distinguished from plain ZIP by
     internal path `xl/workbook.xml`)
   - ODS: `50 4B 03 04` (ZIP container — distinguished by `mimetype` entry)
   - XLS: `D0 CF 11 E0` (OLE2 compound document)
   - gzip: `1F 8B`
   - bzip2: `42 5A 68` (`BZh`)

2. **Extension fallback** — if magic bytes are inconclusive (e.g., plain text
   formats like CSV), the extension determines the reader.

**Mismatch rejection**: if the magic-byte-detected format contradicts the
declared extension, the job fails at stage 1 with `error_code=FORMAT_MISMATCH`.
For example, a gzip file renamed to `.csv` will fail at receive.

---

## 6. Edge cases and limits

| Scenario | Behaviour |
|----------|-----------|
| File > `FLYQUERY_MAX_FILE_MB` | Rejected at upload with `413 Content Too Large` |
| ZIP with multiple entries | Rejected at stage 1 with `error_code=ZIP_MULTI_ENTRY` |
| Zip bomb (decompressed > size cap) | Rejected at stage 1 after decompression size check |
| Empty CSV (only header, zero data rows) | Materialised as a 0-row Parquet; job succeeds with warning |
| All-null column | Profiled as `null_fraction=1.0`; type remains DuckDB inferred type |
| Column name collision (duplicate header) | Second occurrence is renamed `col_n` where n is the 1-based index; `WARN` event emitted |
| 0-byte file | Rejected at stage 1 with `error_code=EMPTY_FILE` |
| Very long column names (>255 chars) | Truncated to 255 chars; `WARN` event emitted |
| Non-UTF-8 table names (XLSX sheet names) | Sanitised to ASCII; non-ASCII characters replaced with `_` |
| Parquet with Decimal128 columns | Preserved as DuckDB DECIMAL; embedded and sampled |
| Avro with recursive schemas | Unsupported; fails at parse with `error_code=UNSUPPORTED_SCHEMA` |
