# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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


import bpy
import ifcopenshell
import ifcopenshell.util.element
import bonsai.tool as tool
import bonsai.core.covering as core


class AddInstanceFlooringCoveringFromCursor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_instance_flooring_covering_from_cursor"
    bl_label = "Add Flooring From Cursor"
    bl_options = {"REGISTER"}
    bl_description = "Add a typed instance flooring covering from cursor position. Move the cursor position into the desired position, select the right space collection and run the operator"

    @classmethod
    def poll(cls, context):
        return tool.Covering.covering_poll_relating_type_check(cls, context, "FLOORING")

    def _execute(self, context):
        try:
            core.add_instance_flooring_covering_from_cursor(tool.Ifc, tool.Root, tool.Spatial)
        except core.NoDefaultContainer:
            return self.report({"ERROR"}, "Please set a default container to create the covering in.")


class AddInstanceCeilingCoveringFromCursor(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_instance_ceiling_covering_from_cursor"
    bl_label = "Add Ceiling From Cursor"
    bl_options = {"REGISTER"}
    bl_description = "Add a typed instance ceiling covering from cursor position. Move the cursor position into the desired position, select the right space collection and run the operator"

    @classmethod
    def poll(cls, context):
        return tool.Covering.covering_poll_relating_type_check(cls, context, "CEILING")

    def _execute(self, context):
        try:
            core.add_instance_ceiling_covering_from_cursor(tool.Ifc, tool.Root, tool.Covering, tool.Spatial)
        except core.NoDefaultContainer:
            return self.report({"ERROR"}, "Please set a default container to create the covering in.")


class RegenSelectedCoveringObject(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.regen_selected_covering_object"
    bl_label = "Regen"
    bl_options = {"REGISTER"}
    bl_description = "Regen selected covering object"

    @classmethod
    def poll(cls, context):
        if (obj := context.active_object) and (element := tool.Ifc.get_entity(obj)) and element.is_a("IfcCovering"):
            return True
        cls.poll_message_set("IfcCovering must be selected.")
        return False

    def _execute(self, context):
        try:
            core.regen_selected_covering_object(tool.Root, tool.Spatial)
        except core.NoDefaultContainer:
            return self.report({"ERROR"}, "Please set a default container to create the covering in.")


class AddInstanceFlooringCoveringsFromWalls(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_instance_flooring_coverings_from_walls"
    bl_label = "Add Flooring From Walls"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Add instance flooring coverings from selected walls. The active object must be a wall and layered vertically"
    )

    @classmethod
    def poll(cls, context):
        return tool.Covering.covering_poll_wall_selected(cls, context, "FLOORING")

    def _execute(self, context):
        # This only works based on a 2D plan only considering the standard
        # walls (i.e. prismatic) in the active object storey.
        # In order to run, the active object must be a wall and
        # there must be selected walls

        try:
            core.add_instance_flooring_coverings_from_walls(tool.Root, tool.Spatial)
        except core.NoDefaultContainer:
            return self.report({"ERROR"}, "Please set a default container to create the covering in.")


class AddInstanceCeilingCoveringsFromWalls(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_instance_ceiling_coverings_from_walls"
    bl_label = "Add Ceiling From Walls"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Add instance ceiling coverings from selected walls. The active object must be a wall and layered vertically"
    )

    @classmethod
    def poll(cls, context):
        return tool.Covering.covering_poll_wall_selected(cls, context, "CEILING")

    def _execute(self, context):
        # This only works based on a 2D plan only considering the standard
        # walls (i.e. prismatic) in the active object storey.
        # In order to run, the active object must be a wall and
        # there must be selected walls

        try:
            core.add_instance_ceiling_coverings_from_walls(tool.Root, tool.Spatial, tool.Covering)
        except core.NoDefaultContainer:
            return self.report({"ERROR"}, "Please set a default container to create the covering in.")
