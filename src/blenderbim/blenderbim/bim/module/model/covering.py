# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell
import blenderbim.tool as tool
import blenderbim.core.covering as core


class AddInstanceFlooringCoveringsFromWalls(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_instance_flooring_coverings_from_walls"
    bl_label = "Add Typed Covering From Walls"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add instance flooring coverings from selected walls. The active object must be a wall and layered vertically"

    @classmethod
    def poll(cls, context):
        active_obj = bpy.context.active_object
        element = tool.Ifc.get_entity(active_obj)
        if element:
            if element.is_a("IfcWall") and tool.Model.get_usage_type(element) == "LAYER2":
                return context.selected_objects

    def _execute(self, context):
        # This only works based on a 2D plan only considering the standard
        # walls (i.e. prismatic) in the active object storey.
        # In order to run, the active object must be a wall and
        # there must be selected walls

        active_obj = bpy.context.active_object
        if not active_obj:
            self.report({"ERROR"}, "No active object. Please select a wall")
            return

        element = tool.Ifc.get_entity(active_obj)
        if element and not element.is_a("IfcWall"):
            return self.report({"ERROR"}, "The active object is not a wall. Please select a wall.")

        container = ifcopenshell.util.element.get_container(element)
        if not container:
            self.report({"ERROR"}, "The wall is not contained.")

        if not bpy.context.selected_objects:
            self.report({"ERROR"}, "No selected objects found. Please select walls.")
            return

        core.add_instance_flooring_coverings_from_walls(tool.Ifc, tool.Spatial, tool.Collector, tool.Geometry)

