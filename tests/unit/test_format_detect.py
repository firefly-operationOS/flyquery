# Copyright 2026 Firefly Software Solutions Inc
import pytest
from flyquery.core.services.ingestion.format_detect import detect_format


@pytest.mark.parametrize(
    "name,head,expected",
    [
        ("orders.csv", b"order_id,total\n1,2\n", ("csv", "none")),
        ("data.tsv", b"a\tb\n1\t2\n", ("tsv", "none")),
        ("x.xlsx", b"PK\x03\x04", ("xlsx", "none")),
        ("x.json", b'{"a":1}', ("json", "none")),
        ("x.jsonl", b'{"a":1}\n{"a":2}\n', ("jsonl", "none")),
        ("x.parquet", b"PAR1", ("parquet", "none")),
        ("x.avro", b"Obj\x01", ("avro", "none")),
        ("x.csv.gz", b"\x1f\x8b", ("csv", "gz")),
        ("x.csv.zip", b"PK\x03\x04", ("csv", "zip")),
        ("x.csv.bz2", b"BZh", ("csv", "bz2")),
        ("x.orc", b"ORC", ("orc", "none")),
        ("x.feather", b"ARROW1", ("arrow", "none")),
        ("x.arrow", b"ARROW", ("arrow", "none")),
    ],
)
def test_detect(name, head, expected):
    assert detect_format(name, head) == expected
