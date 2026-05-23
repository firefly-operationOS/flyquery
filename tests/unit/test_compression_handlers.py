import gzip
import bz2
import zipfile
import pytest
from pathlib import Path
from flyquery.core.services.ingestion.compression import decompress_to_temp, _sync


@pytest.mark.asyncio
async def test_gz_round_trip(tmp_path):
    src = tmp_path / "data.csv.gz"
    payload = b"col_a,col_b\n1,hello\n2,world\n"
    with gzip.open(src, "wb") as f:
        f.write(payload)
    out = await decompress_to_temp(str(src), compression="gz")
    assert Path(out).read_bytes() == payload


@pytest.mark.asyncio
async def test_bz2_round_trip(tmp_path):
    src = tmp_path / "data.csv.bz2"
    payload = b"col_a,col_b\n1,alpha\n2,beta\n"
    with bz2.open(src, "wb") as f:
        f.write(payload)
    out = await decompress_to_temp(str(src), compression="bz2")
    assert Path(out).read_bytes() == payload


@pytest.mark.asyncio
async def test_zip_single_file_ok(tmp_path):
    src = tmp_path / "data.csv.zip"
    payload = b"x,y\n1,2\n"
    with zipfile.ZipFile(src, "w") as zf:
        zf.writestr("data.csv", payload)
    out = await decompress_to_temp(str(src), compression="zip")
    assert Path(out).read_bytes() == payload


@pytest.mark.asyncio
async def test_zip_multifile_raises(tmp_path):
    src = tmp_path / "multi.zip"
    with zipfile.ZipFile(src, "w") as zf:
        zf.writestr("a.csv", "1\n")
        zf.writestr("b.csv", "2\n")
    with pytest.raises(ValueError, match="multiple files"):
        await decompress_to_temp(str(src), compression="zip")


@pytest.mark.asyncio
async def test_none_compression_copies(tmp_path):
    src = tmp_path / "data.csv"
    payload = b"a,b\n1,2\n"
    src.write_bytes(payload)
    out = await decompress_to_temp(str(src), compression="none")
    assert Path(out).read_bytes() == payload


def test_unknown_compression_raises(tmp_path):
    src = tmp_path / "data.xz"
    src.write_bytes(b"junk")
    with pytest.raises(ValueError, match="unknown compression"):
        _sync(str(src), "xz")
