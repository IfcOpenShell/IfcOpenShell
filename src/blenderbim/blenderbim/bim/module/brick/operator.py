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
from blenderbim.tool.brick import BrickStore

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
            element=tool.Ifc.get_entity(context.active_object),
            library=tool.Ifc.get().by_id(int(props.libraries)),
            brick_uri=props.bricks[props.active_brick_index].uri,
        )


class AddBrick(bpy.types.Operator, Operator):
    bl_idname = "bim.add_brick"
    bl_label = "Add Brick"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = context.scene.BIMBrickProperties
        library = None
        if props.libraries:
            library = tool.Ifc.get().by_id(int(props.libraries))
        core.add_brick(
            tool.Ifc,
            tool.Brick,
            element=tool.Ifc.get_entity(context.active_object) if context.selected_objects else None,
            namespace=props.namespace,
            brick_class=props.brick_equipment_class,
            library=library,
        )


class AddBrickFeed(bpy.types.Operator, Operator):
    bl_idname = "bim.add_brick_feed"
    bl_label = "Add Brick Feed"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        source = tool.Ifc.get_entity([o for o in context.selected_objects if o != context.active_object][0])
        destination = tool.Ifc.get_entity(context.active_object)
        core.add_brick_feed(
            tool.Ifc,
            tool.Brick,
            source=source,
            destination=destination,
        )


class ConvertIfcToBrick(bpy.types.Operator, Operator):
    bl_idname = "bim.convert_ifc_to_brick"
    bl_label = "Convert IFC To Brick"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = context.scene.BIMBrickProperties
        library = None
        if props.libraries:
            library = tool.Ifc.get().by_id(int(props.libraries))
        core.convert_ifc_to_brick(tool.Brick, namespace=props.namespace, library=library)


class NewBrickFile(bpy.types.Operator, Operator):
    bl_idname = "bim.new_brick_file"
    bl_label = "New Brick File"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.new_brick_file(tool.Brick)


class RefreshBrickViewer(bpy.types.Operator, Operator):
    bl_idname = "bim.refresh_brick_viewer"
    bl_label = "Refresh Brick Viewer"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.refresh_brick_viewer(tool.Brick)


class RemoveBrick(bpy.types.Operator, Operator):
    bl_idname = "bim.remove_brick"
    bl_label = "Remove Brick"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        props = context.scene.BIMBrickProperties
        core.remove_brick(
            tool.Ifc,
            tool.Brick,
            library=tool.Ifc.get().by_id(int(props.libraries)) if props.libraries else None,
            brick_uri=props.bricks[props.active_brick_index].uri,
        )

class UndoBrick(bpy.types.Operator, Operator):
    bl_idname = "bim.undo_brick"
    bl_label = "Undo Brick"

    def _execute(self, context):
        core.undo_brick(tool.Brick)

class RedoBrick(bpy.types.Operator, Operator):
    bl_idname = "bim.redo_brick"
    bl_label = "Redo Brick"

    def _execute(self, context):
        core.redo_brick(tool.Brick)

class SerializeBrick(bpy.types.Operator, Operator):
    bl_idname = "bim.serialize_brick"
    bl_label = "Serialize Brick"
    filter_glob: bpy.props.StringProperty(default="*.ttl", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    should_save_as: bpy.props.BoolProperty(name="Should Save As", default=False, options={"HIDDEN"})

    def invoke(self, context, event):
        if self.should_save_as or not BrickStore.path:
            WindowManager = context.window_manager
            WindowManager.fileselect_add(self)
            return {"RUNNING_MODAL"}
        else:
            return self.execute(context)

    def _execute(self, context):
        if self.should_save_as or not BrickStore.path:
            BrickStore.path = self.filepath
        core.serialize_brick(tool.Brick)
        return {"FINISHED"}
    
    @classmethod
    def description(cls, context, properties):
        if properties.should_save_as:
            return "Save Brick project to a selected file"
        return "Save the Brick project"