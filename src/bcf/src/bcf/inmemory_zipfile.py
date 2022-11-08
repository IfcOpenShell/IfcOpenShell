"""
In Memory Zip File management, taken from ruamel.std.zipfile

Copyright (c) 2017-2020 Anthon van der Neut, Ruamel bvba

original idea from https://stackoverflow.com/a/19722365/1307905
"""
import zipfile
from io import BytesIO
from os import PathLike
from pathlib import Path
from typing import Any, Optional, Protocol


class ZipFileInterface(Protocol):
    def writestr(self, filename_in_zip: str | zipfile.ZipInfo, file_contents: bytes | str) -> None:
        ...


class InMemoryZipFile:
    def __init__(
        self, file_name: Optional[str | Path] = None, compression: int = zipfile.ZIP_DEFLATED, debug: int = 0
    ) -> None:
        # Create the in-memory file-like object
        self._file_name: Optional[str | Path] = str(file_name) if hasattr(file_name, "_from_parts") else file_name
        self.in_memory_data = BytesIO()
        # Create the in-memory zipfile
        self.in_memory_zip = zipfile.ZipFile(self.in_memory_data, "w", compression, False)
        self.in_memory_zip.debug = debug

    def writestr(self, filename_in_zip: str | zipfile.ZipInfo, file_contents: bytes | str) -> None:
        """Appends a file with name filename_in_zip and contents of
        file_contents to the in-memory zip."""
        self.in_memory_zip.writestr(filename_in_zip, file_contents)

    def write_to_file(self, filename: str | bytes | PathLike[str] | PathLike[bytes] | int) -> None:
        """Writes the in-memory zip to a file."""
        # Mark the files as having been created on Windows so that
        # Unix permissions are not inferred as 0000
        for zfile in self.in_memory_zip.filelist:
            zfile.create_system = 0
        self.in_memory_zip.close()
        with open(filename, "wb") as f:
            f.write(self.data)

    @property
    def data(self) -> bytes:
        return self.in_memory_data.getvalue()

    def __enter__(self) -> "InMemoryZipFile":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        if self._file_name:
            self.write_to_file(self._file_name)
