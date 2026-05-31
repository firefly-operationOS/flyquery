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

"""Transparent decompression for upload-time format chain."""

from __future__ import annotations

import asyncio
import bz2
import gzip
import os
import shutil
import tempfile
import zipfile
from pathlib import Path

MAX_DECOMPRESSED_BYTES = 5 * 1024 * 1024 * 1024  # 5 GB safety cap


async def decompress_to_temp(source_path: str, compression: str) -> str:
    """Decompress *source_path* into a temp file and return the temp path.

    The caller is responsible for deleting the returned temp file when done.
    """
    return await asyncio.to_thread(_sync, source_path, compression)


def _sync(source_path: str, compression: str) -> str:
    p = Path(source_path)
    # Determine the inner extension (strip the compression suffix).
    if compression == "gz" or compression == "bz2":
        inner_ext = p.stem.rsplit(".", 1)[-1] if "." in p.stem else ".bin"
        if not inner_ext.startswith("."):
            inner_ext = f".{inner_ext}"
    elif compression == "zip":
        inner_ext = ".bin"
    elif compression == "none":
        inner_ext = p.suffix or ".bin"
    else:
        raise ValueError(f"unknown compression {compression!r}")

    # We only need the path, then we hand it to ``gzip.open`` / ``bz2.open`` /
    # ``zipfile`` to populate. ``mkstemp`` gives us that without the open file
    # handle that SIM115 would otherwise rightly complain about.
    fd, out_path = tempfile.mkstemp(suffix=inner_ext)
    os.close(fd)

    if compression == "gz":
        with gzip.open(source_path, "rb") as src, open(out_path, "wb") as dst:
            _bounded_copy(src, dst, MAX_DECOMPRESSED_BYTES)
    elif compression == "bz2":
        with bz2.open(source_path, "rb") as src, open(out_path, "wb") as dst:
            _bounded_copy(src, dst, MAX_DECOMPRESSED_BYTES)
    elif compression == "zip":
        with zipfile.ZipFile(source_path, "r") as zf:
            files = [n for n in zf.namelist() if not n.endswith("/")]
            if len(files) != 1:
                raise ValueError(f"zip must contain exactly one file; got multiple files: {files}")
            with zf.open(files[0]) as src, open(out_path, "wb") as dst:
                _bounded_copy(src, dst, MAX_DECOMPRESSED_BYTES)
    elif compression == "none":
        shutil.copyfile(source_path, out_path)

    return out_path


def _bounded_copy(src, dst, cap: int) -> None:
    total = 0
    while True:
        chunk = src.read(64 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > cap:
            raise ValueError(f"decompressed size exceeded cap ({cap} bytes)")
        dst.write(chunk)
