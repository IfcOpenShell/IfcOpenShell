# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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
import json
import logging
import ifcdiff
import ifcopenshell
import bonsai.bim.handler
import bonsai.bim.import_ifc
import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore


class SelectDiffJsonFile(bpy.types.Operator):
    bl_idname = "bim.select_diff_json_file"
    bl_label = "Select Diff JSON File"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.json", options={"HIDDEN"})

    def execute(self, context):
        context.scene.DiffProperties.diff_json_file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class VisualiseDiff(bpy.types.Operator):
    bl_idname = "bim.visualise_diff"
    bl_label = "Visualise Diff"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        ifc_file = tool.Ifc.get()
        with open(context.scene.DiffProperties.diff_json_file, "r") as file:
            diff = json.load(file)
        for obj in context.visible_objects:
            obj.color = (1.0, 1.0, 1.0, 1.0)

            if "IfcDiff Deleted Elements" in obj.users_collection[0].name:
                obj.color = (1.0, 0.0, 0.0, 1.0)
                continue
            elif "IfcDiff Added Elements" in obj.users_collection[0].name:
                obj.color = (0.0, 1.0, 0.0, 1.0)
                continue
            elif "IfcDiff Changed Elements" in obj.users_collection[0].name:
                obj.color = (0.0, 0.0, 0.7, 1.0)
                continue

            if not obj.BIMObjectProperties.ifc_definition_id:
                continue

            ifc_file = ""
            for scene in obj.users_scene:
                if scene.BIMProperties.ifc_file:
                    ifc_file = scene.BIMProperties.ifc_file
                    if scene.library:
                        break

            if ifc_file:
                if ifc_file not in IfcStore.session_files:
                    IfcStore.session_files[ifc_file] = ifcopenshell.open(ifc_file)
                element_file = IfcStore.session_files[ifc_file]
            else:
                element_file = ifc_file

            try:
                element = element_file.by_id(obj.BIMObjectProperties.ifc_definition_id)
            except:
                continue
            global_id = getattr(element, "GlobalId", None)
            if not global_id:
                continue
            if global_id in diff["deleted"]:
                obj.color = (1.0, 0.0, 0.0, 1.0)
            elif global_id in diff["added"]:
                obj.color = (0.0, 1.0, 0.0, 1.0)
            elif global_id in diff["changed"]:
                obj.color = (0.0, 0.0, 1.0, 1.0)
        area = next(area for area in context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].shading.color_type = "OBJECT"
        return {"FINISHED"}


class SelectDiffOldFile(bpy.types.Operator):
    bl_idname = "bim.select_diff_old_file"
    bl_label = "Select Diff Old File"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.ifc", options={"HIDDEN"})

    def execute(self, context):
        context.scene.DiffProperties.old_file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SelectDiffNewFile(bpy.types.Operator):
    bl_idname = "bim.select_diff_new_file"
    bl_label = "Select Diff New File"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.ifc", options={"HIDDEN"})

    def execute(self, context):
        context.scene.DiffProperties.new_file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ExecuteIfcDiff(bpy.types.Operator):
    bl_idname = "bim.execute_ifc_diff"
    bl_label = "Execute IFC Diff"
    filename_ext = ".json"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.json", options={"HIDDEN"})

    def invoke(self, context, event):
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".json")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        import ifcdiff

        self.props = context.scene.DiffProperties

        if tool.Ifc.get():
            if self.props.active_file == "NONE":
                old = ifcopenshell.open(self.props.old_file)
                new = ifcopenshell.open(self.props.new_file)
            elif self.props.active_file == "NEW":
                old = ifcopenshell.open(self.props.old_file)
                new = tool.Ifc.get()
            elif self.props.active_file == "OLD":
                old = tool.Ifc.get()
                new = ifcopenshell.open(self.props.new_file)
        else:
            old = ifcopenshell.open(self.props.old_file)
            new = ifcopenshell.open(self.props.new_file)

        relationships = [r.relationship for r in self.props.diff_relationships]
        query = tool.Search.export_filter_query(self.props.filter_groups) or None

        ifc_diff = ifcdiff.IfcDiff(old, new, relationships=relationships, filter_elements=query)
        ifc_diff.diff()
        ifc_diff.export(self.filepath)
        self.props.diff_json_file = self.filepath

        self.load_changed_elements(ifc_diff)

        bonsai.bim.handler.refresh_ui_data()
        return {"FINISHED"}

    def load_changed_elements(self, ifc_diff: ifcdiff.IfcDiff):
        if not tool.Ifc.get() or self.props.active_file == "NONE" or not self.props.should_load_changed_elements:
            return

        active_ifc = tool.Ifc.get()
        logger = logging.getLogger("ImportIFC")
        ifc_import_settings = bonsai.bim.import_ifc.IfcImportSettings.factory(bpy.context, None, logger)
        ifc_importer = bonsai.bim.import_ifc.IfcImporter(ifc_import_settings)

        if self.props.active_file == "NEW":
            tool.Ifc.set(ifc_diff.old)
            ifc_importer.file = ifc_diff.old
            ifc_importer.process_context_filter()
            ifc_importer.create_styles()

            elements = {ifc_diff.old.by_guid(guid) for guid in ifc_diff.deleted_elements}
            ifc_importer.create_generic_elements(elements)
            self.place_objs_in_collection(ifc_importer.added_data.values(), "IfcDiff Deleted Elements")

            ifc_importer.added_data = {}

            elements = {ifc_diff.old.by_guid(guid) for guid in ifc_diff.change_register.keys()}
            ifc_importer.create_generic_elements(elements)
            self.place_objs_in_collection(ifc_importer.added_data.values(), "IfcDiff Changed Elements")
        elif self.props.active_file == "OLD":
            tool.Ifc.set(ifc_diff.new)
            ifc_importer.file = ifc_diff.new
            ifc_importer.process_context_filter()
            ifc_importer.create_styles()

            elements = {ifc_diff.new.by_guid(guid) for guid in ifc_diff.added_elements}
            ifc_importer.create_generic_elements(elements)
            self.place_objs_in_collection(ifc_importer.added_data.values(), "IfcDiff Added Elements")

            ifc_importer.added_data = {}

            elements = {ifc_diff.new.by_guid(guid) for guid in ifc_diff.change_register.keys()}
            ifc_importer.create_generic_elements(elements)
            self.place_objs_in_collection(ifc_importer.added_data.values(), "IfcDiff Changed Elements")
        tool.Ifc.set(active_ifc)

    def place_objs_in_collection(self, objs, name):
        collection = bpy.data.collections.get(name)
        if not collection:
            collection = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(collection)

        for obj in objs:
            if isinstance(obj, bpy.types.Object):
                collection.objects.link(obj)


class SelectDiffObjects(bpy.types.Operator):
    bl_idname = "bim.select_diff_objects"
    bl_label = "Select Diff Objects"
    bl_options = {"REGISTER", "UNDO"}
    mode: bpy.props.StringProperty()

    def execute(self, context):
        ifc_file = tool.Ifc.get()
        with open(context.scene.DiffProperties.diff_json_file, "r") as file:
            diff = json.load(file)
        for obj in context.visible_objects:
            obj.select_set(False)

            if self.mode == "DELETED" and "IfcDiff Deleted Elements" in obj.users_collection[0].name:
                obj.select_set(True)
                continue
            elif self.mode == "ADDED" and "IfcDiff Added Elements" in obj.users_collection[0].name:
                obj.select_set(True)
                continue
            elif self.mode == "CHANGED" and "IfcDiff Changed Elements" in obj.users_collection[0].name:
                obj.select_set(True)
                continue

            if not obj.BIMObjectProperties.ifc_definition_id:
                continue

            ifc_file = ""
            for scene in obj.users_scene:
                if scene.BIMProperties.ifc_file:
                    ifc_file = scene.BIMProperties.ifc_file
                    if scene.library:
                        break

            if ifc_file:
                if ifc_file not in IfcStore.session_files:
                    IfcStore.session_files[ifc_file] = ifcopenshell.open(ifc_file)
                element_file = IfcStore.session_files[ifc_file]
            else:
                element_file = ifc_file

            try:
                element = element_file.by_id(obj.BIMObjectProperties.ifc_definition_id)
            except:
                continue
            global_id = getattr(element, "GlobalId", None)
            if not global_id:
                continue
            if self.mode == "DELETED" and global_id in diff["deleted"]:
                obj.select_set(True)
            elif self.mode == "ADDED" and global_id in diff["added"]:
                obj.select_set(True)
            elif self.mode == "CHANGED" and global_id in diff["changed"]:
                obj.select_set(True)
        return {"FINISHED"}
