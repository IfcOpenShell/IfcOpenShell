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

from pathlib import Path
import pytest
import ifcopenshell


TEST_FILE_DIR = Path("../../test/input/")


class TestOpen:
    def test_open_ifcspf(self):
        assert ifcopenshell.open(TEST_FILE_DIR / "WallInstance_IFC4Add2.ifc")

    @pytest.mark.skip("IFC-XML temporarily disabled")
    def test_open_ifcxml(self):
        assert ifcopenshell.open(TEST_FILE_DIR / "wall-with-opening-and-window.ifcxml")

    @pytest.mark.skip("IFC-XML temporarily disabled")
    def test_open_ifc_zip_ifcxml_format(self):
        assert ifcopenshell.open(TEST_FILE_DIR / "wall-with-opening-and-window_ifcxml_format.ifczip")

    def test_open_ifc_zip_ifcspf_format(self):
        assert ifcopenshell.open(TEST_FILE_DIR / "WallInstance_IFC4Add2_ifcspf_format.ifczip")

    def test_open_zip(self):
        assert ifcopenshell.open(TEST_FILE_DIR / "WallInstance_IFC4Add2_ifcspf_format.zip")

    def test_open_anyextension_ifcspf_format(self):
        assert ifcopenshell.open(TEST_FILE_DIR / "WallInstance_IFC4Add2_ifcspf_format.anyextension")

    def test_open_anyextension_ifczip_ifcspf_format(self):
        assert ifcopenshell.open(
            TEST_FILE_DIR / "WallInstance_IFC4Add2_ifczip_ifcspf_format.anyextension",
            ".ifcZIP",
        )

    @pytest.mark.skip("IFC-XML temporarily disabled")
    def test_open_anyextension_ifcxml_format(self):
        assert ifcopenshell.open(
            TEST_FILE_DIR / "wall-with-opening-and-window_ifcxml_format.anyextension",
            ".ifcXML",
        )

    @pytest.mark.skip("IFC-XML temporarily disabled")
    def test_invalid_ifcspf(self):
        with pytest.raises(ifcopenshell.Error):
            assert ifcopenshell.open(TEST_FILE_DIR / "invalid.ifc")

    @pytest.mark.skip("IFC-XML temporarily disabled")
    def test_invalid_ifcxml(self):
        with pytest.raises(IOError):
            assert ifcopenshell.open(TEST_FILE_DIR / "invalid.ifcxml")
