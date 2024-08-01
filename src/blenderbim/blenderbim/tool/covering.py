# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import bmesh
import shapely
import ifcopenshell
import ifcopenshell.util.element
import blenderbim.core.tool
import blenderbim.core.root
import blenderbim.core.spatial
import blenderbim.core.geometry
import blenderbim.tool as tool
import json
from math import pi
from mathutils import Vector, Matrix
from shapely import Polygon, MultiPolygon


class Covering(blenderbim.core.tool.Covering):
    @classmethod
    def get_z_from_ceiling_height(cls) -> float:
        props = bpy.context.scene.BIMCoveringProperties
        return props.ceiling_height

    #    def toggle_spaces_visibility_wired_and_textured(cls, spaces):
    #        first_obj = tool.Ifc.get_object(spaces[0])
    #        if bpy.data.objects[first_obj.name].display_type == "TEXTURED":
    #            for space in spaces:
    #                obj = tool.Ifc.get_object(space)
    #                bpy.data.objects[obj.name].show_wire = True
    #                bpy.data.objects[obj.name].display_type = "WIRE"
    #            return
    #
    #        elif bpy.data.objects[first_obj.name].display_type == "WIRE":
    #            for space in spaces:
    #                obj = tool.Ifc.get_object(space)
    #                bpy.data.objects[obj.name].show_wire = False
    #                bpy.data.objects[obj.name].display_type = "TEXTURED"
    #            return

    @classmethod
    def covering_poll_wall_selected(
        cls, operator: type[bpy.types.Operator], context: bpy.types.Context, covering_type: str
    ) -> bool:
        if not context.selected_objects or not context.active_object:
            operator.poll_message_set("No objects selected.")
            return False
        element = tool.Ifc.get_entity(context.active_object)
        if not element or not element.is_a("IfcWall") or not tool.Model.get_usage_type(element) == "LAYER2":
            operator.poll_message_set("LAYER2 based IfcWall must be selected.")
            return False
        return cls.covering_poll_relating_type_check(operator, context, covering_type)

    @classmethod
    def covering_poll_relating_type_check(
        cls, operator: type[bpy.types.Operator], context: bpy.types.Context, covering_type: str
    ) -> bool:
        relating_type_id = int(context.scene.BIMModelProperties.relating_type_id)
        relating_type = ifcopenshell.util.element.get_predefined_type(tool.Ifc.get().by_id(relating_type_id))
        if relating_type != covering_type:
            operator.poll_message_set(f"Select IfcCoveringType with predefined type '{covering_type}'.")
            return False
        return True
