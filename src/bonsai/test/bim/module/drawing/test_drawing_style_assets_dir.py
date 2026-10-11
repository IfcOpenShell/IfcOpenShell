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
import ifcopenshell.util.element
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewIfc

pytestmark = pytest.mark.drawing

PATH_PROPERTIES = {
    "stylesheet_path": "default.css",
    "schedules_stylesheet_path": "schedule.css",
    "markers_path": "markers.svg",
    "symbols_path": "symbols.svg",
    "patterns_path": "patterns.svg",
    "shadingstyles_path": "shading_styles.json",
}


@pytest.fixture
def doc_prefs():
    prefs = tool.Blender.get_addon_preferences().doc
    original = {name: getattr(prefs, name) for name in [*PATH_PROPERTIES, "assets_dir"]}
    yield prefs
    for name, value in original.items():
        setattr(prefs, name, value)


class TestApplyDrawingAssetsDir(NewIfc):
    def test_one_folder_fills_all_six_style_paths(self, doc_prefs):
        doc_prefs.assets_dir = "/office/styles"

        bpy.ops.bim.apply_drawing_assets_dir()

        for name, filename in PATH_PROPERTIES.items():
            assert getattr(doc_prefs, name) == f"/office/styles/{filename}"


class TestOverrideDrawingStyles(NewIfc):
    def test_every_checked_drawing_receives_the_new_style_paths(self, doc_prefs):
        tool.Project.save_test_project()
        bpy.ops.bim.load_drawings()
        bpy.ops.bim.add_drawing()
        bpy.ops.bim.add_drawing()
        bpy.ops.bim.load_drawings()
        bpy.ops.bim.toggle_target_view(option="EXPAND", target_view="PLAN_VIEW")
        props = tool.Drawing.get_document_props()
        props.active_drawing_index = next(i for i, item in enumerate(props.drawings) if item.is_drawing)
        doc_prefs.assets_dir = "/office/styles"
        bpy.ops.bim.apply_drawing_assets_dir()

        bpy.ops.bim.override_drawing_styles(override_all=True)

        drawings = tool.Ifc.get().by_type("IfcAnnotation")
        assert len(drawings) == 2
        for drawing in drawings:
            pset = ifcopenshell.util.element.get_pset(drawing, "EPset_Drawing")
            assert pset["Stylesheet"] == "/office/styles/default.css"
            assert pset["Markers"] == "/office/styles/markers.svg"
            assert pset["Symbols"] == "/office/styles/symbols.svg"
            assert pset["Patterns"] == "/office/styles/patterns.svg"
            assert pset["ShadingStyles"] == "/office/styles/shading_styles.json"
