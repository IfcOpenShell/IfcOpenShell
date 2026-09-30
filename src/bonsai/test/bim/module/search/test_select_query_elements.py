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

import bonsai.tool as tool
from test.bim.bootstrap import NewIfc


def add_element(ifc_class):
    bpy.ops.mesh.primitive_cube_add()
    obj = bpy.context.active_object
    root_props = tool.Root.get_root_props()
    root_props.ifc_product = "IfcElement"
    root_props.ifc_class = ifc_class
    bpy.ops.bim.assign_class()
    return obj


def add_wall_and_slab_with_wall_selected():
    wall = add_element("IfcWall")
    slab = add_element("IfcSlab")
    tool.Blender.set_objects_selection(bpy.context, wall, [wall])
    return wall, slab


class TestSelectQueryElements(NewIfc):
    def test_clearing_the_previous_selection_leaves_only_the_query_results(self):
        wall, slab = add_wall_and_slab_with_wall_selected()
        bpy.ops.bim.select_query_elements(query="IfcSlab", clear_previous_selection=True)
        assert set(bpy.context.selected_objects) == {slab}
        assert bpy.context.active_object == slab

    def test_default_adds_the_query_results_to_the_selection(self):
        wall, slab = add_wall_and_slab_with_wall_selected()
        bpy.ops.bim.select_query_elements(query="IfcSlab")
        assert set(bpy.context.selected_objects) == {wall, slab}
        assert bpy.context.active_object == wall
