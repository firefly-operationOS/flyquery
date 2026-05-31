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

import gzip
from pathlib import Path

import pytest

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
    from flyquery.core.services.ingestion.reader import TableExtractionRules
    from flyquery.core.services.ingestion.readers.csv_reader import CsvReader

    out = await decompress_to_temp(str(FIX / "orders.csv.gz"), compression="gz")
    r = CsvReader()
    tables = await r.enumerate_tables(out, TableExtractionRules())
    assert tables[0].n_columns == 4
