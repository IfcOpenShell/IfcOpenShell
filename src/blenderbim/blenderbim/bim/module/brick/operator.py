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
import ifcopenshell.api
import blenderbim.tool as tool
import blenderbim.core.brick as core
import blenderbim.bim.handler
from blenderbim.bim.ifc import IfcStore


class Operator:
    def execute(self, context):
        self._execute(context)
        blenderbim.bim.handler.refresh_ui_data()
        return {"FINISHED"}


class LoadBrickProject(bpy.types.Operator, Operator):
    bl_idname = "bim.load_brick_project"
    bl_label = "Load Brickschema Project"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.ttl", options={"HIDDEN"})

    def _execute(self, context):
        core.load_brick_project(tool.Brick, filepath=self.filepath)

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ViewBrickClass(bpy.types.Operator, Operator):
    bl_idname = "bim.view_brick_class"
    bl_label = "View Brick Class"
    bl_options = {"REGISTER", "UNDO"}
    brick_class: bpy.props.StringProperty(name="Brick Class")

    def _execute(self, context):
        core.view_brick_class(tool.Brick, brick_class=self.brick_class)


class ViewBrickItem(bpy.types.Operator, Operator):
    bl_idname = "bim.view_brick_item"
    bl_label = "View Brick Item"
    bl_options = {"REGISTER", "UNDO"}
    item: bpy.props.StringProperty(name="Brick Item")

    def _execute(self, context):
        core.view_brick_item(tool.Brick, item=self.item)


class RewindBrickClass(bpy.types.Operator, Operator):
    bl_idname = "bim.rewind_brick_class"
    bl_label = "Rewind Brick Class"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.rewind_brick_class(tool.Brick)


class CloseBrickProject(bpy.types.Operator, Operator):
    bl_idname = "bim.close_brick_project"
    bl_label = "Close Brick Project"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.close_brick_project(tool.Brick)


class ConvertBrickProject(bpy.types.Operator, Operator):
    bl_idname = "bim.convert_brick_project"
    bl_label = "Convert Brick Project"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.convert_brick_project(tool.Ifc, tool.Brick)


class AssignBrickReference(bpy.types.Operator, Operator):
    bl_idname = "bim.assign_brick_reference"
    bl_label = "Assign Brick Reference"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = context.scene.BIMBrickProperties
        core.assign_brick_reference(
            tool.Ifc,
            tool.Brick,
            obj=context.active_object,
            library=tool.Ifc.get().by_id(int(props.libraries)),
            brick_uri=props.bricks[props.active_brick_index].uri,
        )
