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
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.util.representation

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestAxisLinework(NewFile):
    def count_axis_groups(self, has_axis_linework: bool) -> int:
        bpy.ops.bim.create_project()
        tool.Project.save_test_project()
        ifc = tool.Ifc.get()

        bpy.ops.mesh.primitive_cube_add(size=4, location=(0, 0, 1.5))
        bpy.ops.bim.assign_class(ifc_class="IfcWall")
        wall = ifc.by_type("IfcWall")[0]
        plan = ifcopenshell.util.representation.get_context(ifc, "Plan") or ifcopenshell.api.context.add_context(
            ifc, "Plan"
        )
        axis_context = ifcopenshell.api.context.add_context(ifc, "Plan", "Axis", "GRAPH_VIEW", parent=plan)
        axis = ifcopenshell.api.geometry.add_axis_representation(
            ifc, context=axis_context, axis=[(-2.0, 0.0), (2.0, 0.0)]
        )
        ifcopenshell.api.geometry.assign_representation(ifc, product=wall, representation=axis)

        bpy.ops.bim.load_drawings()
        bpy.ops.bim.add_drawing()
        drawing = ifc.by_type("IfcAnnotation")[0]
        bpy.ops.bim.activate_drawing(drawing=drawing.id())
        camera_props = tool.Drawing.get_camera_props(bpy.context.scene.camera)
        camera_props.has_axis_linework = has_axis_linework
        bpy.ops.bim.create_drawing()

        svg = ET.parse(Path(tool.Ifc.get_path()).parent / "drawings" / "PLAN_VIEW.svg").getroot()
        return len([g for g in svg.iter("{http://www.w3.org/2000/svg}g") if "axis" in g.get("class", "").split()])

    def test_axis_reference_lines_are_drawn_when_enabled(self):
        assert self.count_axis_groups(True) == 1

    def test_axis_reference_lines_are_off_by_default(self):
        assert self.count_axis_groups(False) == 0
