# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import zipfile
from typing import IO, Union, TypedDict
from typing_extensions import NotRequired


class HeaderMetadata(TypedDict):
    name: NotRequired[str]
    # FILE_DESCRIPTION, not the description from FILE_NAME.
    description: NotRequired[str]
    implementation_level: NotRequired[str]
    time_stamp: NotRequired[str]
    schema_name: NotRequired[str]


class IfcHeaderExtractor:
    """An utility class for extracting header information from IFC files.

    This class provides functionality to extract key metadata from the header section of
    IFC files without recreating the entire file as `ifcopenshell.file`.
    For optimization, extractor will search only for the first 50 lines
    of the IFC file for metadata.

    Supported formats: .ifc, .ifczip.

    Metadata available by the extraction is presented in the example below.


    Example:

    .. code:: python

        from ifcopenshell.util.file import IfcHeaderExtractor

        extractor = IfcHeaderExtractor("path/to/your/file.ifc")
        # Get dictionary of the extracted metadata.
        header_info = extractor.extract()

        # Print the extracted information

        # ViewDefinition[DesignTransferView]
        print("File Description:", header_info.get("description"))

        # 2;1
        print("Implementation Level:", header_info.get("implementation_level"))

        # file.ifc
        print("File Name:", header_info.get("name"))

        # 2024-06-25T15:48:10+05:00
        print("Time Stamp:", header_info.get("time_stamp"))

        # IFC4X3_ADD2
        print("Schema Name:", header_info.get("schema_name"))
    """

    def __init__(self, filepath: str):
        self.filepath = filepath

    def extract(self) -> HeaderMetadata:
        extension = self.filepath.split(".")[-1]
        if extension.lower() == "ifc":
            with open(self.filepath) as ifc_file:
                return self.extract_ifc_spf(ifc_file)
        elif extension.lower() == "ifczip":
            return self.extract_ifc_zip()
        elif extension.lower() == "ifcsqlite":
            return {}  # TODO
        raise ValueError(f"Unsupported file extension: '{extension}'.")

    def extract_ifc_spf(self, ifc_file: Union[IO[bytes], IO[str]]) -> HeaderMetadata:
        # https://www.steptools.com/stds/step/IS_final_p21e3.html#clause-8
        data = HeaderMetadata()
        max_lines_to_parse = 50
        for _ in range(max_lines_to_parse):
            line = next(ifc_file)
            if isinstance(line, bytes):
                line = line.decode("utf-8")
            if line.startswith("FILE_DESCRIPTION"):
                for i, part in enumerate(line.split("'")):
                    if i == 1:
                        data["description"] = part
                    elif i == 3:
                        data["implementation_level"] = part
            elif line.startswith("FILE_NAME"):
                for i, part in enumerate(line.split("'")):
                    if i == 1:
                        data["name"] = part
                    elif i == 3:
                        data["time_stamp"] = part
            elif line.startswith("FILE_SCHEMA"):
                data["schema_name"] = line.split("'")[1]
                break
        return data

    def extract_ifc_zip(self) -> HeaderMetadata:
        archive = zipfile.ZipFile(self.filepath, "r")
        return self.extract_ifc_spf(archive.open(archive.filelist[0]))
