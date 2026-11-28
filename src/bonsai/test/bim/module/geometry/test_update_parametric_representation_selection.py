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


def add_wall():
    bpy.ops.mesh.primitive_cube_add()
    obj = bpy.context.active_object
    root_props = tool.Root.get_root_props()
    root_props.ifc_product = "IfcElement"
    root_props.ifc_class = "IfcWall"
    bpy.ops.bim.assign_class()
    return obj


def add_extruded_wall():
    obj = add_wall()
    bpy.ops.bim.update_representation(ifc_representation_class="IfcExtrudedAreaSolid/IfcRectangleProfileDef")
    return obj


def depth_of(obj):
    return tool.Ifc.get_entity(obj).Representation.Representations[0].Items[0].Depth


class TestUpdateParametricRepresentation(NewIfc):
    def test_editing_a_parameter_applies_to_the_matching_selected_objects(self):
        first = add_extruded_wall()
        second = add_extruded_wall()
        tessellated = add_wall()
        representation = tool.Ifc.get_entity(tessellated).Representation
        tool.Blender.set_objects_selection(bpy.context, first, [first, second, tessellated])
        bpy.ops.bim.get_representation_ifc_parameters()
        parameters = tool.Geometry.get_mesh_props(first.data).ifc_parameters
        index = next(i for i, p in enumerate(parameters) if p.name == "IfcExtrudedAreaSolid/Depth")
        parameters[index].value = 7.0
        assert bpy.ops.bim.update_parametric_representation(index=index) == {"FINISHED"}
        assert depth_of(first) == 7.0
        assert depth_of(second) == 7.0
        assert tool.Ifc.get_entity(tessellated).Representation == representation
