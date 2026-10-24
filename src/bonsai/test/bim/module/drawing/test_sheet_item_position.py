# This file was generated with the assistance of an AI coding tool.
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

import xml.etree.ElementTree as ET
from pathlib import Path

import bpy

import bonsai.tool as tool
from bonsai.bim.module.drawing.sheeter import SVG, SheetBuilder
from test.bim.bootstrap import NewFile


class TestSheetItemPosition(NewFile):
    def test_set_and_get_position_of_a_drawing_on_a_sheet(self):
        bpy.ops.bim.create_project()
        tool.Project.save_test_project()
        ifc = tool.Ifc.get()
        layout_path = Path(tool.Ifc.get_path()).parent / "layouts" / "A01 - UNTITLED.svg"
        props = tool.Drawing.get_document_props()

        bpy.ops.bim.load_sheets()
        bpy.ops.bim.add_sheet()
        bpy.ops.bim.load_drawings()
        for d in props.drawings:
            d.is_expanded = True
        bpy.ops.bim.add_drawing()
        drawing = ifc.by_type("IfcAnnotation")[0]
        for i, d in enumerate(props.drawings):
            if d.ifc_definition_id == drawing.id():
                props.active_drawing_index = i
        bpy.ops.bim.activate_drawing(drawing=drawing.id())
        bpy.ops.bim.create_drawing()
        bpy.ops.bim.add_drawing_to_sheet()

        root = ET.parse(layout_path).getroot()
        reference = ifc.by_id(int(root.findall(f'{SVG}g[@data-type="drawing"]')[0].attrib["data-id"]))
        sheet = tool.Drawing.get_reference_document(reference)
        builder = SheetBuilder()

        assert builder.set_sheet_item_position(reference, sheet, 100.0, 50.0)

        assert tuple(builder.get_sheet_item_position(reference, sheet)) == (100.0, 50.0)
