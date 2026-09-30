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

from pathlib import Path

import bpy

import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore
from test.bim.bootstrap import NewIfc


def add_drawing_to_a_sheet(ifc_path):
    bpy.ops.bim.save_project(filepath=str(ifc_path), should_save_as=True)
    bpy.ops.bim.load_drawings()
    bpy.ops.bim.add_drawing()
    bpy.ops.bim.toggle_target_view(option="EXPAND", target_view="PLAN_VIEW")
    drawing_props = tool.Drawing.get_document_props()
    drawing_props.active_drawing_index = next(i for i, d in enumerate(drawing_props.drawings) if d.is_drawing)
    bpy.ops.bim.activate_drawing(drawing=drawing_props.drawings[drawing_props.active_drawing_index].ifc_definition_id)
    bpy.ops.bim.create_drawing()
    bpy.ops.bim.load_sheets()
    bpy.ops.bim.add_sheet()
    sheet = tool.Ifc.get().by_type("IfcDocumentInformation")[-1]
    bpy.ops.bim.expand_sheet(sheet=sheet.id())
    bpy.ops.bim.add_drawing_to_sheet()
    return sheet


def remove_drawing_from_sheet(sheet):
    props = tool.Drawing.get_document_props()
    props.active_sheet_index = next(
        i for i, s in enumerate(props.sheets) if not s.is_sheet and s.reference_type != "TITLEBLOCK"
    )
    layout = Path(tool.Drawing.get_document_uri(sheet, "LAYOUT"))
    with_drawing = layout.read_text()
    key_before = IfcStore.history[-1]["key"]
    bpy.ops.bim.remove_drawing_from_sheet(reference=props.sheets[props.active_sheet_index].ifc_definition_id)
    without_drawing = layout.read_text()
    assert without_drawing != with_drawing
    return layout, with_drawing, without_drawing, key_before, IfcStore.history[-1]["key"]


class TestRemoveDrawingFromSheet(NewIfc):
    def test_undo_and_redo_follow_the_drawing_removal(self, tmp_path):
        sheet = add_drawing_to_a_sheet(tmp_path / "model.ifc")
        layout, with_drawing, without_drawing, key_before, key_removal = remove_drawing_from_sheet(sheet)
        IfcStore.undo(until_key=key_before)
        assert layout.read_text() == with_drawing
        IfcStore.redo(until_key=key_removal)
        assert layout.read_text() == without_drawing
