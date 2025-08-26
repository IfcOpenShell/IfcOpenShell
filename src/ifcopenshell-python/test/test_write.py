# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Thomas Krijnen <thomas@aecgeeks.com>
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

import tempfile
from pathlib import Path
import pytest
import ifcopenshell


TEST_FILE_DIR = Path("../../test/input/")


class TestWrite:
    model: ifcopenshell.file

    def setup_method(self):
        self.model = ifcopenshell.open(TEST_FILE_DIR / "WallInstance_IFC4Add2.ifc")

    def assert_model_is_written(self, filename, format=None, zipped=False):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / filename
            self.model.write(file_path, format, zipped)
            assert file_path.exists()

    def test_write_ifcspf(self):
        self.assert_model_is_written("model.ifc")

    def test_write_ifcxml(self):
        self.assert_model_is_written("model.ifcXML")

    def test_write_ifc_zip_ifcxml_format(self):
        self.assert_model_is_written("model.ifcZIP", format=".ifcXML", zipped=True)

    def test_write_ifc_zip_ifcspf_format(self):
        self.assert_model_is_written("model.ifcZIP")

    def test_write_zip(self):
        self.assert_model_is_written("model.zip", format=".ifcZIP")

    def test_write_anyextension_ifcspf_format(self):
        self.assert_model_is_written("model.anyextension", format=".ifc")

    def test_write_anyextension_ifczip_ifcspf_format(self):
        self.assert_model_is_written("model.anyextension", format=".ifc", zipped=True)

    def test_write_anyextension_ifcxml_format(self):
        self.assert_model_is_written("model.anyextension", format=".ifcXML")

    def test_write_anyextension_ifczip_ifcxml_format(self):
        self.assert_model_is_written("model.anyextension", format=".ifcXML", zipped=True)

    def test_write_to_non_existing_dir(self):
        self.assert_model_is_written("tmp/model.ifczip")
