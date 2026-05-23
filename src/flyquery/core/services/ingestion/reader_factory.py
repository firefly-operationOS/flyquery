# Copyright 2026 Firefly Software Solutions Inc
"""FileReader dispatch.

Selection is by (format, compression). Compression is handled by decorating
the underlying reader with a decompression layer at the adapter boundary;
each reader operates on a decompressed path.
"""

from __future__ import annotations

from flyquery.core.services.ingestion.reader import FileReader, UnsupportedFormatError

_SUPPORTED_COMPRESSIONS = frozenset({"none", "gz", "zip", "bz2"})


def get_reader(file_format: str, compression: str = "none") -> FileReader:
    if compression not in _SUPPORTED_COMPRESSIONS:
        raise UnsupportedFormatError(
            f"compression {compression!r} not in {sorted(_SUPPORTED_COMPRESSIONS)}"
        )
    fmt = file_format.lower()
    if fmt in ("csv", "tsv"):
        from flyquery.core.services.ingestion.readers.csv_reader import CsvReader

        return CsvReader()
    if fmt in ("xlsx", "xls", "ods"):
        from flyquery.core.services.ingestion.readers.excel_reader import ExcelReader

        return ExcelReader()
    if fmt in ("json", "jsonl"):
        from flyquery.core.services.ingestion.readers.json_reader import JsonReader

        return JsonReader()
    if fmt == "parquet":
        from flyquery.core.services.ingestion.readers.parquet_reader import ParquetReader

        return ParquetReader()
    if fmt == "avro":
        from flyquery.core.services.ingestion.readers.avro_reader import AvroReader

        return AvroReader()
    if fmt == "orc":
        from flyquery.core.services.ingestion.readers.orc_reader import OrcReader

        return OrcReader()
    if fmt in ("arrow", "feather"):
        from flyquery.core.services.ingestion.readers.arrow_reader import ArrowReader

        return ArrowReader()
    raise UnsupportedFormatError(f"format {fmt!r} not supported")
