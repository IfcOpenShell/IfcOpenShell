import bpy
import ifccsv
import ifcopenshell
import json
from blenderbim.bim.ifc import IfcStore



class SelectDiffJsonFile(bpy.types.Operator):
    bl_idname = "bim.select_diff_json_file"
    bl_label = "Select Diff JSON File"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.DiffProperties.diff_json_file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class VisualiseDiff(bpy.types.Operator):
    bl_idname = "bim.visualise_diff"
    bl_label = "Visualise Diff"

    def execute(self, context):
        #ifc_file = IfcStore.get_file() # In case we get from Store
        ifc_file = ifcopenshell.open(context.scene.DiffProperties.diff_new_file) # for Now refer to the new file
        with open(bpy.context.scene.DiffProperties.diff_json_file, "r") as file:
            diff = json.load(file)
        for obj in bpy.context.visible_objects:
            obj.color = (1.0, 1.0, 1.0, 0.2)
            global_id = ifc_file.by_id(obj.BIMObjectProperties.ifc_definition_id).GlobalId
            #global_id = obj.BIMObjectProperties.attributes.get("GlobalId")
            if not global_id:
                continue
            if global_id.string_value in diff["deleted"]:
                obj.color = (1.0, 0.0, 0.0, 0.2)
            elif global_id.string_value in diff["added"]:
                obj.color = (0.0, 1.0, 0.0, 0.2)
            elif global_id.string_value in diff["changed"]:
                obj.color = (0.0, 0.0, 1.0, 0.2)
        area = next(area for area in bpy.context.screen.areas if area.type == "VIEW_3D")
        area.spaces[0].shading.color_type = "OBJECT"
        return {"FINISHED"}


class SelectDiffOldFile(bpy.types.Operator):
    bl_idname = "bim.select_diff_old_file"
    bl_label = "Select Diff Old File"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.DiffProperties.diff_old_file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class SelectDiffNewFile(bpy.types.Operator):
    bl_idname = "bim.select_diff_new_file"
    bl_label = "Select Diff New File"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        bpy.context.scene.DiffProperties.diff_new_file = self.filepath
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class ExecuteIfcDiff(bpy.types.Operator):
    bl_idname = "bim.execute_ifc_diff"
    bl_label = "Execute IFC Diff"
    filename_ext = ".json"
    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def invoke(self, context, event):
        self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".json")
        WindowManager = context.window_manager
        WindowManager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        import ifcdiff

        ifc_diff = ifcdiff.IfcDiff(
            bpy.context.scene.DiffProperties.diff_old_file,
            bpy.context.scene.DiffProperties.diff_new_file,
            self.filepath,
            bpy.context.scene.DiffProperties.diff_relationships.split(),
        )
        ifc_diff.diff()
        ifc_diff.export()
        bpy.context.scene.DiffProperties.diff_json_file = self.filepath
        return {"FINISHED"}
