import gzip
import pytest
from pathlib import Path
from flyquery.core.services.ingestion.compression import decompress_to_temp

FIX = Path(__file__).parent / "fixtures"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_gzip_decompresses(tmp_path):
    src = tmp_path / "x.csv.gz"
    with gzip.open(src, "wb") as f:
        f.write(b"a,b,c\n1,2,3\n4,5,6\n")
    out = await decompress_to_temp(str(src), compression="gz")
    assert Path(out).read_bytes() == b"a,b,c\n1,2,3\n4,5,6\n"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_zip_rejects_multifile(tmp_path):
    import zipfile

    src = tmp_path / "x.zip"
    with zipfile.ZipFile(src, "w") as zf:
        zf.writestr("a.csv", "1\n")
        zf.writestr("b.csv", "2\n")
    with pytest.raises(ValueError, match="multiple files"):
        await decompress_to_temp(str(src), compression="zip")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_gz_fixture_decompresses_to_csv(tmp_path):
    """Verify orders.csv.gz decompresses and is parseable by CsvReader."""
    from flyquery.core.services.ingestion.readers.csv_reader import CsvReader
    from flyquery.core.services.ingestion.reader import TableExtractionRules

    out = await decompress_to_temp(str(FIX / "orders.csv.gz"), compression="gz")
    r = CsvReader()
    tables = await r.enumerate_tables(out, TableExtractionRules())
    assert tables[0].n_columns == 4
