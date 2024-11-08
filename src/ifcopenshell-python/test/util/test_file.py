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

import pytest
import test.bootstrap
import ifcopenshell.util.file as subject
import tempfile
import zipfile
from pathlib import Path


HEADER_EXTRACTOR_TEST_FILE_STR = """
ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('ViewDefinition[DesignTransferView]'),'2;1');
FILE_NAME('file.ifc','2024-06-25T15:48:10+05:00',(),(),'IfcOpenShell 0.0.0','Bonsai 0.0.999999-xxxxxxx','Nobody');
FILE_SCHEMA(('IFC4X3_ADD2'));
ENDSEC;
DATA;
#1=IFCPROJECT('1U7MoqHmr8YP6jwz0pc7e0',$,'My Project',$,$,$,$,(#14,#26),#9);
ENDSEC;
END-ISO-10303-21;
"""


class TestExtractHeaderMetadata(test.bootstrap.IFC4):
    def check_metadata_fields(self, filepath: str) -> None:
        extractor = subject.IfcHeaderExtractor(filepath)
        header_info = extractor.extract()
        assert header_info.get("description") == "ViewDefinition[DesignTransferView]"
        assert header_info.get("implementation_level") == "2;1"
        assert header_info.get("name") == "file.ifc"
        assert header_info.get("time_stamp") == "2024-06-25T15:48:10+05:00"
        assert header_info.get("schema_name") == "IFC4X3_ADD2"

    def get_ifc_filepath(self) -> Path:
        temp_dir = Path(tempfile.gettempdir())
        filepath = temp_dir / "test.ifc"
        with open(filepath, "w") as fo:
            fo.write(HEADER_EXTRACTOR_TEST_FILE_STR)
        return filepath

    def test_ifc(self) -> None:
        self.check_metadata_fields(str(self.get_ifc_filepath()))

    def test_ifc_zip(self) -> None:
        ifc_filepath = self.get_ifc_filepath()
        zip_filepath = ifc_filepath.with_suffix(".ifczip")
        with zipfile.ZipFile(zip_filepath, mode="w") as zf:
            zf.write(str(ifc_filepath))
        self.check_metadata_fields(str(zip_filepath))
