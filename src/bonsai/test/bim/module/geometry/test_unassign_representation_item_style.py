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
import ifcopenshell.api.style

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestUnassignRepresentationItemStyleWithRepresentationlessSelection(NewFile):
    def test_run(self):
        bpy.ops.bim.create_project()
        ifc = tool.Ifc.get()
        bpy.ops.mesh.primitive_cube_add()
        wall_obj = bpy.context.active_object
        bpy.ops.bim.assign_class(obj=wall_obj.name, ifc_class="IfcWall")
        space_obj = bpy.data.objects.new("Space", None)
        bpy.context.scene.collection.objects.link(space_obj)
        bpy.ops.bim.assign_class(obj=space_obj.name, ifc_class="IfcSpace")
        assert tool.Ifc.get_entity(space_obj).Representation is None

        bpy.ops.object.select_all(action="DESELECT")
        wall_obj.select_set(True)
        bpy.context.view_layer.objects.active = wall_obj
        bpy.ops.bim.enable_editing_representation_items()
        props = tool.Geometry.get_object_geometry_props(wall_obj)
        item = ifc.by_id(props.active_item.ifc_definition_id)
        style = ifcopenshell.api.style.add_style(ifc, name="Style")
        tool.Style.assign_style_to_representation_item(item, style)

        space_obj.hide_viewport = False
        space_obj.select_set(True)
        bpy.context.view_layer.objects.active = wall_obj
        assert bpy.ops.bim.unassign_representation_item_style() == {"FINISHED"}
        assert tool.Style.get_representation_item_style(item) is None
