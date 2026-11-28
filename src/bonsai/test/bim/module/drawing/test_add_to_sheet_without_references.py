# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.
#
# This file was generated with the assistance of an AI coding tool.

import bpy
import ifcopenshell.api.document
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestAddToSheetWithoutDocumentReferences(NewFile):
    def _setup(self, scope):
        bpy.ops.bim.create_project()
        tool.Project.save_test_project()
        ifc = tool.Ifc.get()
        document = ifcopenshell.api.document.add_information(ifc)
        document.Name = "Document"
        document.Scope = scope
        bpy.ops.bim.load_sheets()
        bpy.ops.bim.add_sheet()
        sheet = next(d for d in ifc.by_type("IfcDocumentInformation") if d.Scope == "SHEET")
        return document, sheet

    def test_schedule(self):
        schedule, sheet = self._setup("SCHEDULE")
        bpy.ops.bim.load_schedules()
        references_before = len(tool.Drawing.get_document_references(sheet))
        with pytest.raises(RuntimeError, match="The schedule must be generated"):
            bpy.ops.bim.add_schedule_to_sheet()
        assert len(tool.Drawing.get_document_references(sheet)) == references_before

    def test_reference(self):
        reference, sheet = self._setup("REFERENCE")
        bpy.ops.bim.load_references()
        references_before = len(tool.Drawing.get_document_references(sheet))
        with pytest.raises(RuntimeError, match="The reference must be generated"):
            bpy.ops.bim.add_reference_to_sheet()
        assert len(tool.Drawing.get_document_references(sheet)) == references_before
