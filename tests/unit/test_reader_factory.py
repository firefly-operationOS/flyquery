import pytest
from flyquery.core.services.ingestion.reader_factory import get_reader
from flyquery.core.services.ingestion.reader import UnsupportedFormatError


def test_factory_dispatches_csv():
    r = get_reader(file_format="csv", compression="none")
    assert r.__class__.__name__ == "CsvReader"


def test_factory_dispatches_xlsx():
    r = get_reader(file_format="xlsx", compression="none")
    assert r.__class__.__name__ == "ExcelReader"


def test_factory_dispatches_parquet():
    r = get_reader(file_format="parquet", compression="none")
    assert r.__class__.__name__ == "ParquetReader"


def test_factory_raises_on_unknown_format():
    with pytest.raises(UnsupportedFormatError):
        get_reader(file_format="rar", compression="none")


def test_factory_raises_on_unknown_compression():
    with pytest.raises(UnsupportedFormatError):
        get_reader(file_format="csv", compression="rar")
