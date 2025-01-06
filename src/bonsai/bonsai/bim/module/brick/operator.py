# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import os
import bpy
import ifcopenshell.api
import bonsai.tool as tool
import bonsai.core.brick as core
import bonsai.bim.handler
from bonsai.bim.ifc import IfcStore
from bonsai.tool.brick import BrickStore


class LoadBrickProject(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.load_brick_project"
    bl_label = "Load Brickschema Project"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Load in a Brick project from a file"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.ttl", options={"HIDDEN"})

    def _execute(self, context):
        if os.path.exists(self.filepath) and "ttl" in os.path.splitext(self.filepath)[1].lower():
            root = context.scene.BIMBrickProperties.brick_list_root
            core.load_brick_project(tool.Brick, filepath=self.filepath, brick_root=root)
        else:
            self.report({"ERROR"}, f"Failed to load {self.filepath}")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ViewBrickClass(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.view_brick_class"
    bl_label = "View Brick Class"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Inspect the subclasses of this class"
    brick_class: bpy.props.StringProperty(name="Brick Class")
    split_screen: bpy.props.BoolProperty(name="Split Screen", default=False, options={"HIDDEN"})

    def _execute(self, context):
        core.view_brick_class(tool.Brick, brick_class=self.brick_class, split_screen=self.split_screen)


class ViewBrickItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.view_brick_item"
    bl_label = "View Brick Item"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Inspect this entity in the viewer"
    item: bpy.props.StringProperty(name="Brick Item")
    split_screen: bpy.props.BoolProperty(name="Split Screen", default=False, options={"HIDDEN"})

    def _execute(self, context):
        try:
            core.view_brick_item(tool.Brick, item=self.item, split_screen=self.split_screen)
        except:
            self.report({"ERROR"}, f"Could not find {self.item}")


class RewindBrickClass(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.rewind_brick_class"
    bl_label = "Rewind Brick Class"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Go back to the previous list view"
    split_screen: bpy.props.BoolProperty(name="Split Screen", default=False, options={"HIDDEN"})

    def _execute(self, context):
        core.rewind_brick_class(tool.Brick, split_screen=self.split_screen)


class CloseBrickProject(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.close_brick_project"
    bl_label = "Close Brick Project"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Close the Brick project"

    def _execute(self, context):
        core.close_brick_project(tool.Brick)


class ConvertBrickProject(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.convert_brick_project"
    bl_label = "Convert Brick Project"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Create an Ifc library for this Brick project"

    def _execute(self, context):
        core.convert_brick_project(tool.Ifc, tool.Brick)


class AssignBrickReference(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_brick_reference"
    bl_label = "Assign Brick Reference"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Assign the selected Ifc entity to the selected Brick entity"

    def _execute(self, context):
        if not context.active_object:
            self.report({"ERROR"}, f"No Ifc selected")
            return
        props = context.scene.BIMBrickProperties
        try:
            props.bricks[props.active_brick_index]
        except:
            self.report({"ERROR"}, f"No Brick selected")
            return
        core.assign_brick_reference(
            tool.Ifc,
            tool.Brick,
            element=tool.Ifc.get_entity(context.active_object),
            library=tool.Ifc.get().by_id(int(props.libraries)),
            brick_uri=props.bricks[props.active_brick_index].uri,
        )


class AddBrick(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_brick"
    bl_label = "Add Brick"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Create the Brick entity"

    def _execute(self, context):
        props = context.scene.BIMBrickProperties
        core.add_brick(
            tool.Ifc,
            tool.Brick,
            element=tool.Ifc.get_entity(context.active_object) if context.selected_objects else None,
            namespace=props.namespace,
            brick_class=props.brick_entity_class,
            library=tool.Ifc.get().by_id(int(props.libraries)) if props.libraries else None,
            label=props.new_brick_label,
        )


class AddBrickRelation(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_brick_relation"
    bl_label = "Add Brick Relation"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Create the Brick relationship"

    def _execute(self, context):
        props = context.scene.BIMBrickProperties
        brick = props.bricks[props.active_brick_index]
        if props.new_brick_relation_type == "http://www.w3.org/2000/01/rdf-schema#label":
            object = props.new_brick_relation_object
        elif props.split_screen_toggled:
            object = props.split_screen_bricks[props.split_screen_active_brick_index].uri
        else:
            object = props.namespace + props.new_brick_relation_object
        core.add_brick_relation(tool.Brick, brick_uri=brick.uri, predicate=props.new_brick_relation_type, object=object)


class ConvertIfcToBrick(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.convert_ifc_to_brick"
    bl_label = "Convert IFC To Brick"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Convert Ifc entities and relations to Brick entities and relations"

    def _execute(self, context):
        props = context.scene.BIMBrickProperties
        library = None
        if props.libraries:
            library = tool.Ifc.get().by_id(int(props.libraries))
        core.convert_ifc_to_brick(tool.Brick, namespace=props.namespace, library=library)


class NewBrickFile(bpy.types.Operator):
    bl_idname = "bim.new_brick_file"
    bl_label = "New Brick File"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Create a Brick project from scratch"

    def execute(self, context):
        IfcStore.begin_transaction(self)
        IfcStore.add_transaction_operation(self, rollback=self.rollback, commit=lambda data: True)
        self._execute(context)
        self.transaction_data = {
            "schema": BrickStore.schema,
            "path": BrickStore.path,
            "graph": BrickStore.graph,
        }
        IfcStore.add_transaction_operation(self, rollback=lambda data: True, commit=self.commit)
        IfcStore.end_transaction(self)
        bonsai.bim.handler.refresh_ui_data()
        return {"FINISHED"}

    def _execute(self, context):
        root = context.scene.BIMBrickProperties.brick_list_root
        core.new_brick_file(tool.Brick, brick_root=root)

    def rollback(self, data):
        BrickStore.purge()

    def commit(self, data):
        BrickStore.schema = data["schema"]
        BrickStore.path = data["path"]
        BrickStore.graph = data["graph"]


class RefreshBrickViewer(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.refresh_brick_viewer"
    bl_label = "Refresh Brick Viewer"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Refresh the list view"

    def _execute(self, context):
        core.refresh_brick_viewer(tool.Brick)


class RemoveBrick(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_brick"
    bl_label = "Remove Brick"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Delete this entity"

    def _execute(self, context):
        props = context.scene.BIMBrickProperties
        core.remove_brick(
            tool.Ifc,
            tool.Brick,
            library=tool.Ifc.get().by_id(int(props.libraries)) if props.libraries else None,
            brick_uri=props.bricks[props.active_brick_index].uri,
        )


class SerializeBrick(bpy.types.Operator):
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

    def execute(self, context):
        if self.should_save_as or not BrickStore.path:
            BrickStore.path = self.filepath
        core.serialize_brick(tool.Brick)
        return {"FINISHED"}

    @classmethod
    def description(cls, context, properties):
        if properties.should_save_as:
            return "Save Brick project to a selected file"
        return "Save the Brick project"


class AddBrickNamespace(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_brick_namespace"
    bl_label = "Add Brick Namespace"
    bl_description = "Bind a new namespace to the Brick project"

    def _execute(self, context):
        props = context.scene.BIMBrickProperties
        alias = props.new_brick_namespace_alias
        uri = props.new_brick_namespace_uri
        core.add_brick_namespace(tool.Brick, alias=alias, uri=uri)


class RemoveBrickRelation(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_brick_relation"
    bl_label = "Remove Relation"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Delete this relationship"
    predicate: bpy.props.StringProperty(name="Relation")
    object: bpy.props.StringProperty(name="Object")

    def _execute(self, context):
        props = context.scene.BIMBrickProperties
        brick = props.bricks[props.active_brick_index]
        core.remove_brick_relation(tool.Brick, brick_uri=brick.uri, predicate=self.predicate, object=self.object)
