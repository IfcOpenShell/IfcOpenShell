# IfcCSV - A utility to interact with IFC data through CSV.
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcCSV.
#
# IfcCSV is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcCSV is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcCSV.  If not, see <http://www.gnu.org/licenses/>.

import tempfile
import os

import openpyxl
import ifcopenshell
import ifcopenshell.api.root
import ifcopenshell.api.unit

import ifccsv


def setup_project() -> ifcopenshell.file:
    ifc_file = ifcopenshell.file(schema="IFC4")
    ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject")
    ifcopenshell.api.unit.assign_unit(ifc_file)
    return ifc_file


class TestIfcCsv:
    def test_blank_xlsx_cell_does_not_corrupt_attribute(self):
        # Regression test: a blank XLSX/ODS cell is read back by pandas as
        # float `nan`, not as an empty string or None (pandas cannot tell a
        # blank cell apart from a genuinely missing one). Before the fix,
        # `nan` fell through process_row's null/empty checks untouched and
        # was later stringified, silently setting the IFC attribute to the
        # literal text "nan" instead of clearing it - even though the user
        # only deleted a cell's content in Excel.
        ifc_file = setup_project()
        wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall")
        wall.Name = "Original Name"
        wall.Description = "Original Description"

        with tempfile.TemporaryDirectory() as tmp_dir:
            xlsx_path = os.path.join(tmp_dir, "user_edited.xlsx")
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.append(["GlobalId", "Name", "Description"])
            ws.append([wall.GlobalId, "Original Name", None])  # Description cell left blank
            wb.save(xlsx_path)

            ifc_csv = ifccsv.IfcCsv()
            ifc_csv.Import(ifc_file, xlsx_path, attributes=["Name", "Description"])

        assert wall.Description == "", f"expected an empty string, got {wall.Description!r}"

    def test_xlsx_roundtrip_of_empty_string_is_stable(self):
        # Reimporting an unchanged XLSX export should be a no-op, even for an
        # attribute that was explicitly an empty string (as opposed to None).
        ifc_file = setup_project()
        wall = ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcWall")
        wall.Name = ""

        with tempfile.TemporaryDirectory() as tmp_dir:
            xlsx_path = os.path.join(tmp_dir, "export.xlsx")
            ifc_csv = ifccsv.IfcCsv()
            ifc_csv.export(ifc_file, [wall], ["Name"], output=xlsx_path, format="xlsx")

            ifc_csv2 = ifccsv.IfcCsv()
            ifc_csv2.Import(ifc_file, xlsx_path, attributes=["Name"])

        assert wall.Name == "", f"expected an empty string, got {wall.Name!r}"
