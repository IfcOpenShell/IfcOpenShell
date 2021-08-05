import bpy
import importlib
import importlib.util
import ifcpatch
from blenderbim.bim.helper import draw_attributes
from .helper import extract_docs
from .operator import PopulatePatchArguments


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

        row = layout.row(align=True)
        row.prop(props, "ifc_patch_input")
        row.operator("bim.select_ifc_patch_input", icon="FILE_FOLDER", text="")

        row = layout.row(align=True)
        row.prop(props, "ifc_patch_output")
        row.operator("bim.select_ifc_patch_output", icon="FILE_FOLDER", text="")

        op = layout.operator(PopulatePatchArguments.bl_idname)
        op.recipe = recipe
        if props.ifc_patch_args_attr:
            draw_attributes(props.ifc_patch_args_attr, layout, show_description=True)
        else:
            row = layout.row()
            row.prop(props, "ifc_patch_args")
        row = layout.row()
        op = row.operator("bim.execute_ifc_patch")
        op.use_json_for_args = bool(props.ifc_patch_args_attr)
