# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Ryan Schultz
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

# This file was generated with the assistance of an AI coding tool.

import bpy

import bonsai.core.terrain as core
import bonsai.tool as tool


def get_active_terrain(context):
    if not (obj := context.active_object) or obj.type != "MESH":
        return None
    if (element := tool.Ifc.get_entity(obj)) and tool.Terrain.is_terrain(element):
        return element


class GenerateContours(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.generate_contours"
    bl_label = "Generate Contours"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = (
        "Create IfcAnnotation contour lines from the active terrain's top surface, replacing any it already has"
    )

    @classmethod
    def poll(cls, context):
        return get_active_terrain(context) is not None

    def _execute(self, context):
        props = tool.Terrain.get_terrain_props()
        try:
            total = core.generate_contours(
                tool.Terrain,
                get_active_terrain(context),
                interval=props.contour_interval,
                index_interval=props.contour_index_interval,
            )
        except ValueError as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}
        self.report({"INFO"}, f"Created {total} contours")


class UpdateContours(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.update_contours"
    bl_label = "Update Contours"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Regenerate the active terrain's contours from its current shape and saved interval"

    @classmethod
    def poll(cls, context):
        return get_active_terrain(context) is not None

    def _execute(self, context):
        try:
            total = core.update_contours(tool.Terrain, get_active_terrain(context))
        except ValueError as e:
            self.report({"ERROR"}, str(e))
            return {"CANCELLED"}
        self.report({"INFO"}, f"Created {total} contours")


class RemoveContours(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_contours"
    bl_label = "Remove Contours"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Delete the active terrain's contour lines and its saved contour settings"

    @classmethod
    def poll(cls, context):
        return get_active_terrain(context) is not None

    def _execute(self, context):
        core.remove_contours(tool.Terrain, get_active_terrain(context))
