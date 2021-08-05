import bpy
import ifcpatch
from blenderbim.bim.helper import draw_attributes
from .helper import extract_docs
from .operator import PopulatePatchArguments
import json


class BIM_PT_patch(bpy.types.Panel):
    bl_label = "IFC Patch"
    bl_idname = "BIM_PT_patch"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene
        props = scene.BIMPatchProperties
        row = layout.row()
        row.prop(props, "ifc_patch_recipes")
        
        recipe = props.ifc_patch_recipes

        docs = extract_docs(ifcpatch, recipe, "Patcher", "__init__", ("src", "file", "logger", "args"))
        if "description" in docs:
            col = layout.column(align=True)
            for line in docs["description"].split("\n"):
                    col.label(text=line)

        row = layout.row(align=True)
        row.prop(props, "ifc_patch_input")
        row.operator("bim.select_ifc_patch_input", icon="FILE_FOLDER", text="")

        row = layout.row(align=True)
        row.prop(props, "ifc_patch_output")
        row.operator("bim.select_ifc_patch_output", icon="FILE_FOLDER", text="")

        update_args_op = layout.operator(PopulatePatchArguments.bl_idname)
        update_args_op.inputs = json.dumps([
            (
                v["name"], 
                v["type"], 
                v.get("default", None), 
                v.get("description", "")
            ) 
            for v in docs.get("inputs", {}).values()])
        if props.ifc_patch_args_attr and update_args_op.inputs:
            draw_attributes(props.ifc_patch_args_attr, layout, show_description=True)
        else:
            row = layout.row()
            row.prop(props, "ifc_patch_args")

        row = layout.row()
        op = row.operator("bim.execute_ifc_patch")
        op.use_json_for_args = not update_args_op.inputs
