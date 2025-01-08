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

import os
import bpy
import json
import bmesh
import logging
import numpy as np
import ifcopenshell
import bonsai.tool as tool
from math import radians
from mathutils import Matrix, Vector
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.clash.decorator import ClashDecorator


class ExportClashSets(bpy.types.Operator):
    bl_idname = "bim.export_clash_sets"
    bl_label = "Export Clash Sets"
    bl_description = "Export clash sets to a selected file"
    filename_ext = ".json"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.json", options={"HIDDEN"})

    def invoke(self, context, event):
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".json")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        self.filepath = bpy.path.ensure_ext(self.filepath, ".json")
        clash_sets = tool.Clash.export_clash_sets()
        with open(self.filepath, "w") as destination:
            destination.write(json.dumps(clash_sets, indent=4))
        return {"FINISHED"}


class ImportClashSets(bpy.types.Operator):
    bl_idname = "bim.import_clash_sets"
    bl_label = "Import Clash Sets"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Import clash sets from a selected file"
    filename_ext = ".json"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.json", options={"HIDDEN"})

    def invoke(self, context, event):
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".json")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        tool.Clash.load_clash_sets(self.filepath)
        context.scene.BIMClashProperties.clash_sets.clear()
        for clash_set in tool.Clash.get_clash_sets():
            new = context.scene.BIMClashProperties.clash_sets.add()
            new.name = clash_set["name"]
            new.mode = clash_set["mode"]
            if new.mode == "intersection":
                new.tolerance = clash_set["tolerance"]
                new.check_all = clash_set["check_all"]
            elif new.mode == "collision":
                new.allow_touching = clash_set["allow_touching"]
            elif new.mode == "clearance":
                new.clearance = clash_set["clearance"]
                new.check_all = clash_set["check_all"]
            for clash_source in clash_set["a"]:
                new_source = new.a.add()
                new_source.name = clash_source["file"]
                if "selector" in clash_source:
                    tool.Search.import_filter_query(clash_source["selector"], new_source.filter_groups)
                    new_source.mode = clash_source["mode"]
            if "b" in clash_set and clash_set["b"]:
                for clash_source in clash_set["b"]:
                    new_source = new.b.add()
                    new_source.name = clash_source["file"]
                    if "selector" in clash_source:
                        tool.Search.import_filter_query(clash_source["selector"], new_source.filter_groups)
                        new_source.mode = clash_source["mode"]
        tool.Clash.import_active_clashes()
        return {"FINISHED"}


class AddClashSet(bpy.types.Operator):
    bl_idname = "bim.add_clash_set"
    bl_label = "Add Clash Set"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add a clash set"

    def execute(self, context):
        new = context.scene.BIMClashProperties.clash_sets.add()
        new.name = "New Clash Set"
        return {"FINISHED"}


class RemoveClashSet(bpy.types.Operator):
    bl_idname = "bim.remove_clash_set"
    bl_label = "Remove Clash Set"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Remove the selected clash set"
    index: bpy.props.IntProperty()

    def execute(self, context):
        context.scene.BIMClashProperties.clash_sets.remove(self.index)
        return {"FINISHED"}


class AddClashSource(bpy.types.Operator):
    bl_idname = "bim.add_clash_source"
    bl_label = "Add Clash Source"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add a clash source to this group"
    group: bpy.props.StringProperty()

    def execute(self, context):
        clash_set = context.scene.BIMClashProperties.active_clash_set
        source = getattr(clash_set, self.group).add()
        return {"FINISHED"}


class RemoveClashSource(bpy.types.Operator):
    bl_idname = "bim.remove_clash_source"
    bl_label = "Remove Clash Source"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Remove this clash source"
    index: bpy.props.IntProperty()
    group: bpy.props.StringProperty()

    def execute(self, context):
        clash_set = context.scene.BIMClashProperties.active_clash_set
        getattr(clash_set, self.group).remove(self.index)
        return {"FINISHED"}


class SelectClashSource(bpy.types.Operator):
    bl_idname = "bim.select_clash_source"
    bl_label = "Select Clash Source"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Select an IFC file to add as a clash source"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_glob: bpy.props.StringProperty(default="*.ifc", options={"HIDDEN"})
    index: bpy.props.IntProperty()
    group: bpy.props.StringProperty()

    def execute(self, context):
        clash_set = context.scene.BIMClashProperties.active_clash_set
        getattr(clash_set, self.group)[self.index].name = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SelectClashResults(bpy.types.Operator):
    bl_idname = "bim.select_clash_results"
    bl_label = "Select Clash Results"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        context.scene.BIMClashProperties.clash_results_path = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SelectSmartGroupedClashesPath(bpy.types.Operator):
    bl_idname = "bim.select_smart_grouped_clashes_path"
    bl_label = "Select Smart-Grouped Clashes Path"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        context.scene.BIMClashProperties.smart_grouped_clashes_path = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ExecuteIfcClash(bpy.types.Operator):
    bl_idname = "bim.execute_ifc_clash"
    bl_label = "Execute IFC Clash"
    bl_description = "Execute clash detection and save the information to a .bcf or .json file"
    filter_glob: bpy.props.StringProperty(default="*.bcf;*.json", options={"HIDDEN"})
    filepath: bpy.props.StringProperty(subtype="FILE_PATH", options={"SKIP_SAVE"})

    def invoke(self, context, event):
        if self.filepath:
            return self.execute(context)
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        from ifcclash import ifcclash

        self.props = context.scene.BIMClashProperties

        _, extension = os.path.splitext(self.filepath)
        if extension != ".bcf":
            self.filepath = bpy.path.ensure_ext(self.filepath, ".json")
        # TODO Temporarily until BCF support comes back
        if extension != ".json":
            self.filepath = bpy.path.ensure_ext(self.filepath, ".bcf")

        self.props.export_path = self.filepath
        settings = ifcclash.ClashSettings()
        settings.output = self.filepath
        settings.logger = logging.getLogger("Clash")
        settings.logger.setLevel(logging.DEBUG)
        clasher = ifcclash.Clasher(settings)

        if self.props.should_create_clash_snapshots:

            def get_viewpoint_snapshot(viewpoint):
                camera = bpy.data.objects.get("IFC Clash Camera")
                if not camera:
                    camera = bpy.data.objects.new("IFC Clash Camera", bpy.data.cameras.new("IFC Clash Camera"))
                    context.scene.collection.objects.link(camera)

                bcf_camera = viewpoint.visualization_info.perspective_camera
                p = bcf_camera.camera_view_point
                z = bcf_camera.camera_direction
                z = Vector([z.x, z.y, z.z]) * -1
                y = bcf_camera.camera_up_vector
                y = Vector([y.x, y.y, y.z])
                x = y.cross(z)

                mat = Matrix(
                    [
                        [x[0], y[0], z[0], p.x],
                        [x[1], y[1], z[1], p.y],
                        [x[2], y[2], z[2], p.z],
                        [0, 0, 0, 0],
                    ]
                )

                camera.matrix_world = mat
                context.scene.camera = camera
                camera.data.angle = radians(60)
                area = next(area for area in context.screen.areas if area.type == "VIEW_3D")
                area.spaces[0].region_3d.view_perspective = "CAMERA"
                area.spaces[0].shading.show_xray = True
                context.scene.render.resolution_x = 480
                context.scene.render.resolution_y = 270
                context.scene.render.image_settings.file_format = "PNG"
                context.scene.render.filepath = os.path.join(context.scene.BIMProperties.data_dir, "snapshot.png")
                bpy.ops.render.opengl(write_still=True)
                with open(context.scene.render.filepath, "rb") as f:
                    return ("snapshot.png", f.read())

            clasher.get_viewpoint_snapshot = get_viewpoint_snapshot

        clasher.clash_sets = tool.Clash.export_clash_sets()
        clasher.clash()
        clasher.export()

        if extension == ".json":
            tool.Clash.load_clash_sets(self.filepath)
            tool.Clash.import_active_clashes()
        self.report({"INFO"}, "Finished IFC clash.")
        return {"FINISHED"}


class SelectIfcClashResults(bpy.types.Operator):
    bl_idname = "bim.select_ifc_clash_results"
    bl_label = "Select IFC Clash Results"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Select the clashing IFC geometry stored in a file"
    filename_ext = ".json"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".json")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        # TODO refactor into new clash results system
        self.file = IfcStore.get_file()
        self.filepath = bpy.path.ensure_ext(self.filepath, ".json")
        with open(self.filepath) as f:
            clash_sets = json.load(f)
        clash_set_name = context.scene.BIMClashProperties.active_clash_set.name
        global_ids = []
        for clash_set in clash_sets:
            if clash_set["name"] != clash_set_name:
                continue
            if not "clashes" in clash_set.keys():
                self.report({"WARNING"}, "No clashes found for the selected Clash Set.")
                return {"CANCELLED"}
            for clash in clash_set["clashes"].values():
                global_ids.extend([clash["a_global_id"], clash["b_global_id"]])

        for obj in context.visible_objects:
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
                element_file = self.file

            try:
                element = element_file.by_id(obj.BIMObjectProperties.ifc_definition_id)
            except:
                continue

            global_id = getattr(element, "GlobalId", None)
            if not global_id:
                continue
            if global_id in global_ids:
                obj.select_set(True)
        return {"FINISHED"}


class SelectClash(bpy.types.Operator):
    bl_idname = "bim.select_clash"
    bl_label = "Select Clash"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Select the clashing IFC geometry stored in a file"
    index: bpy.props.IntProperty()

    def execute(self, context):
        self.props = context.scene.BIMClashProperties
        clash_set = tool.Clash.get_clash_set(self.props.active_clash_set.name)
        active_clash = self.props.active_clash
        clash = tool.Clash.get_clash(clash_set, active_clash.a_global_id, active_clash.b_global_id)

        if not clash:
            return {"FINISHED"}

        products = []

        for global_id in (clash["a_global_id"], clash["b_global_id"]):
            try:
                products.append(tool.Ifc.get().by_guid(global_id))
            except:
                pass

        tool.Spatial.select_products(products, unhide=True)
        ClashDecorator.install(bpy.context)
        target = Vector(clash["p1"])
        tool.Clash.look_at(target, target + Vector((5, 5, 5)))
        self.props.p1 = clash["p1"]
        self.props.p2 = clash["p2"]
        self.props.active_clash_text = clash["type"].title() + " " + str(round(clash["distance"] * 1000)) + "mm"
        return {"FINISHED"}


class SmartClashGroup(bpy.types.Operator):
    bl_idname = "bim.smart_clash_group"
    bl_label = "Smart Group Clashes"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    @classmethod
    def poll(cls, context):
        return context.scene.BIMClashProperties.clash_results_path

    def execute(self, context):
        from ifcclash import ifcclash

        settings = ifcclash.ClashSettings()
        self.filepath = bpy.path.ensure_ext(context.scene.BIMClashProperties.clash_results_path, ".json")
        settings.output = self.filepath
        settings.logger = logging.getLogger("Clash")
        settings.logger.setLevel(logging.DEBUG)
        ifc_clasher = ifcclash.Clasher(settings)

        with open(self.filepath) as f:
            clash_sets = json.load(f)

        # execute the smart grouping
        save_path = bpy.path.ensure_ext(context.scene.BIMClashProperties.smart_grouped_clashes_path, ".json")
        smart_grouped_clashes = ifc_clasher.smart_group_clashes(
            clash_sets, context.scene.BIMClashProperties.smart_clash_grouping_max_distance
        )

        # save smart_groups to json
        with open(save_path, "w") as f:
            f.write(json.dumps(smart_grouped_clashes))

        clash_set_name = context.scene.BIMClashProperties.active_clash_set.name

        # Reset the list of smart_clash_groups for the UI
        context.scene.BIMClashProperties.smart_clash_groups.clear()

        for clash_set, smart_groups in smart_grouped_clashes.items():
            # Only select the clashes that correspond to the actively selected IFC Clash Set
            if clash_set != clash_set_name:
                continue
            else:
                for smart_group, global_id_pairs in smart_groups[0].items():
                    new_group = context.scene.BIMClashProperties.smart_clash_groups.add()
                    new_group.number = f"{smart_group}"

                    for pair in global_id_pairs:
                        for id in pair:
                            new_global_id = new_group.global_ids.add()
                            new_global_id.name = id

        return {"FINISHED"}


class LoadSmartGroupsForActiveClashSet(bpy.types.Operator):
    bl_idname = "bim.load_smart_groups_for_active_clash_set"
    bl_label = "Load Smart Groups for Active Clash Set"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene.BIMClashProperties.active_clash_set

    def execute(self, context):
        smart_groups_path = bpy.path.ensure_ext(context.scene.BIMClashProperties.smart_grouped_clashes_path, ".json")

        clash_set_name = context.scene.BIMClashProperties.active_clash_set.name

        with open(smart_groups_path) as f:
            smart_grouped_clashes = json.load(f)

        # Reset the list of smart_clash_groups for the UI
        context.scene.BIMClashProperties.smart_clash_groups.clear()

        for clash_set, smart_groups in smart_grouped_clashes.items():
            # Only select the clashes that correspond to the actively selected IFC Clash Set
            if clash_set != clash_set_name:
                continue
            else:
                for smart_group, global_id_pairs in smart_groups[0].items():
                    new_group = context.scene.BIMClashProperties.smart_clash_groups.add()
                    new_group.number = f"{smart_group}"
                    for pair in global_id_pairs:
                        for guid in pair:
                            new_global_id = new_group.global_ids.add()
                            new_global_id.guid = guid

        return {"FINISHED"}


class SelectSmartGroup(bpy.types.Operator):
    bl_idname = "bim.select_smart_group"
    bl_label = "Select Smart Group"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file() and context.visible_objects and context.scene.BIMClashProperties.active_smart_group

    def execute(self, context):
        selected_smart_group = context.scene.BIMClashProperties.active_smart_group
        products = []
        for global_id in selected_smart_group.global_ids:
            try:
                products.append(tool.Ifc.get().by_guid(global_id.guid))
            except:
                continue
        tool.Spatial.select_products(products, unhide=True)
        context_override = tool.Blender.get_viewport_context()
        with bpy.context.temp_override(**context_override):
            bpy.ops.view3d.view_selected()
        return {"FINISHED"}
