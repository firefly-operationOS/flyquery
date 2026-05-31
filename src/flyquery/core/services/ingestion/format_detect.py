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

"""Format detection from magic bytes + file extension."""

from __future__ import annotations


def detect_format(filename: str, head_bytes: bytes) -> tuple[str, str]:
    """Return (format, compression).

    Inspects the file extension first, then falls back to magic-byte sniffing
    for files without a recognised extension.
    """
    name = filename.lower()

    # Compression wrappers — strip and recurse on the inner name.
    if name.endswith(".gz"):
        inner = name[:-3]
        return _format_from_name(inner, head_bytes), "gz"
    if name.endswith(".bz2"):
        inner = name[:-4]
        return _format_from_name(inner, head_bytes), "bz2"
    if name.endswith(".zip"):
        inner = name[:-4]
        fmt = _format_from_name(inner, head_bytes)
        return fmt, "zip"

    return _format_from_name(name, head_bytes), "none"


def _format_from_name(name: str, head: bytes) -> str:
    """Detect format from (lower-cased) filename, with magic-byte fallback."""
    if name.endswith(".csv"):
        return "csv"
    if name.endswith(".tsv"):
        return "tsv"
    if name.endswith(".jsonl") or name.endswith(".ndjson"):
        return "jsonl"
    if name.endswith(".json"):
        return "json"
    if name.endswith(".parquet"):
        return "parquet"
    if name.endswith(".avro"):
        return "avro"
    if name.endswith(".orc"):
        return "orc"
    if name.endswith(".arrow") or name.endswith(".feather"):
        return "arrow"
    if name.endswith(".xlsx"):
        return "xlsx"
    if name.endswith(".xls"):
        return "xls"
    if name.endswith(".ods"):
        return "ods"

    # Magic-byte fallback
    if head.startswith(b"PAR1"):
        return "parquet"
    if head.startswith(b"Obj\x01"):
        return "avro"
    if head.startswith(b"ORC"):
        return "orc"
    # Feather v2 / Arrow IPC magic: b"ARROW1\x00\x00" or b"\xff\xff\xff\xff"
    if head.startswith(b"ARROW1") or head.startswith(b"ARROW"):
        return "arrow"
    # ZIP-based formats: xlsx, ods, zip archive.  The .zip extension case is
    # handled before reaching this function; a bare PK magic here is xlsx/ods.
    if head.startswith(b"PK\x03\x04"):
        return "xlsx"
    if head.startswith(b"{") or head.startswith(b"["):
        return "json"

    raise ValueError(f"could not detect format for {name!r}")
