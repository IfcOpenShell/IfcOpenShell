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
    def get_z_from_ceiling_height(cls):
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
