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
import bonsai.tool as tool
import bonsai.core.spatial as core


class GenerateSpace(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.generate_space"
    bl_label = "Generate Space from Cursor"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Create a space from the cursor position.\n\n"
        "Move the cursor position into the desired position, "
        "set RL value in Spatial Tool (it's a height of the cutting plane to generate space footprint), "
        "select the right default space container and run the operator.\n\n"
        "Note that if object is active, it will be used as a reference point instead of cursor. "
        "If the active object is IfcSpace, it will be reused instead of creating a new IfcSpace"
    )

    def _execute(self, context):
        # This works as a 2.5 extruded polygon based on a cutting plane. Note
        # that rooms exclude walls (i.e. not to wall midpoint or exterior /
        # exterior edge.

        try:
            core.generate_space(tool.Ifc, tool.Model, tool.Root, tool.Spatial, tool.Type)
        except core.SpaceGenerationError as e:
            return self.report({"ERROR"}, str(e))


class GenerateSpacesFromWalls(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.generate_spaces_from_walls"
    bl_label = "Generate Spaces From Walls"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Generate spaces from selected walls. The active object must be a wall"

    def _execute(self, context):
        # This only works based on a 2D plan only considering the standard
        # walls (i.e. prismatic) in the active object storey.
        # In order to run, the active object must be a wall and
        # there must be selected walls

        active_obj = context.active_object
        element = tool.Ifc.get_entity(active_obj)
        container = tool.Spatial.get_container(element)

        def msg_no_active_object(self, context):
            self.layout.label(text="No active object. Please select a wall")

        def msg_no_active_wall(self, context):
            self.layout.label(text="The active object is not a wall. Please select a wall.")

        def msg_no_container(self, context):
            self.layout.label(text="The wall is not contained. Please the selected wall in a building container")

        def msg_no_selected_objects(self, context):
            self.layout.label(text="No selected objects found. Please select walls.")

        if not active_obj:
            context.window_manager.popup_menu(msg_no_active_object, title="Error", icon="ERROR")
            return

        element = tool.Ifc.get_entity(active_obj)
        if element and not element.is_a("IfcWall"):
            context.window_manager.popup_menu(msg_no_active_wall, title="Error", icon="ERROR")
            return

        if not container:
            context.window_manager.popup_menu(msg_no_container, title="Error", icon="ERROR")
            return

        if not context.selected_objects:
            context.window_manager.popup_menu(msg_no_selected_objects, title="Error", icon="ERROR")
            return

        core.generate_spaces_from_walls(tool.Ifc, tool.Spatial, tool.Collector)


class ToggleSpaceVisibility(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.toggle_space_visibility"
    bl_label = "Toggle Space Visibility"
    bl_options = {"REGISTER"}
    bl_description = "Change the space visibility"

    def execute(self, context):
        core.toggle_space_visibility(tool.Ifc, tool.Spatial)
        return {"FINISHED"}


class ToggleHideSpaces(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.toggle_hide_spaces"
    bl_label = "Toggle Hide Spaces"
    bl_options = {"REGISTER"}
    bl_description = "Hide or Unhide all spaces"

    def execute(self, context):
        core.toggle_hide_spaces(tool.Ifc, tool.Spatial)
        return {"FINISHED"}
