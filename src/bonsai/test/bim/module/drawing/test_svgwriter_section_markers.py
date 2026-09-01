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

"""Covers issue #5872: an EPset_Drawing.ShowSheetReferences toggle lets a
drawing hide the sheet-reference line under section/elevation tags, for
projects where every section already lives on one sheet.
"""

import bpy
import ifcopenshell
import ifcopenshell.api.pset
import pytest
from mathutils import Vector

import bonsai.tool as tool
from bonsai.bim.module.drawing.svgwriter import SvgWriter
from test.bim.bootstrap import NewFile

pytestmark = pytest.mark.drawing


def _make_drawing_and_marker(show_sheet_references=None):
    ifc = ifcopenshell.file()
    tool.Ifc.set(ifc)

    drawing = ifc.create_entity("IfcAnnotation", ObjectType="DRAWING")
    pset = ifcopenshell.api.pset.add_pset(ifc, product=drawing, name="EPset_Drawing")
    if show_sheet_references is not None:
        ifcopenshell.api.pset.edit_pset(ifc, pset=pset, properties={"ShowSheetReferences": show_sheet_references})

    camera_data = bpy.data.cameras.new("TestCamera")
    camera_obj = bpy.data.objects.new("TestCamera", camera_data)
    bpy.context.scene.collection.objects.link(camera_obj)
    tool.Ifc.link(drawing, camera_obj)

    marker = ifc.create_entity("IfcAnnotation", ObjectType="SECTION")
    ifc.create_entity("IfcRelAssignsToProduct", RelatedObjects=[marker], RelatingProduct=drawing)

    return camera_obj, marker


def _render_marker_text(camera_obj, marker):
    writer = SvgWriter(camera_width=10, camera_height=10, camera=camera_obj, camera_projection=Vector((0, 0, -1)))
    writer.create_blank_svg("/tmp/test_svgwriter_section_markers.svg")
    writer.draw_marker_reference_text(marker, Vector((100.0, 200.0)), "SECTION")
    return writer.svg.tostring()


class TestShowSheetReferences(NewFile):
    def test_defaults_to_true_when_pset_key_is_absent(self):
        camera_obj, marker = _make_drawing_and_marker(show_sheet_references=None)
        drawing = tool.Ifc.get_entity(camera_obj)
        assert tool.Drawing.show_sheet_references(drawing) is True

    def test_shows_reference_and_sheet_id_by_default(self):
        camera_obj, marker = _make_drawing_and_marker(show_sheet_references=None)
        svg = _render_marker_text(camera_obj, marker)
        assert svg.count("<text") == 2
        # split above and below the marker centre (y=200), unchanged legacy layout.
        assert 'y="197.5"' in svg
        assert 'y="202.5"' in svg

    def test_hides_sheet_id_and_recenters_reference_id_when_disabled(self):
        camera_obj, marker = _make_drawing_and_marker(show_sheet_references=False)
        svg = _render_marker_text(camera_obj, marker)
        assert svg.count("<text") == 1
        assert 'y="200.0"' in svg

    def test_toggle_applies_to_elevation_markers_too(self):
        camera_obj, marker = _make_drawing_and_marker(show_sheet_references=False)
        writer = SvgWriter(camera_width=10, camera_height=10, camera=camera_obj, camera_projection=Vector((0, 0, -1)))
        writer.create_blank_svg("/tmp/test_svgwriter_section_markers.svg")
        writer.draw_marker_reference_text(marker, Vector((50.0, 60.0)), "ELEVATION")
        svg = writer.svg.tostring()
        assert svg.count("<text") == 1
        assert 'y="60.0"' in svg
