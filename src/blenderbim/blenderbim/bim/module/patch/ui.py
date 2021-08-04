import bpy
import importlib
import importlib.util
import ifcpatch
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

        op = layout.operator(PopulatePatchArguments.bl_idname)
        op.recipe = recipe
        if props.ifc_patch_args_attr and bool(docs["inputs"]):
            for attr in props.ifc_patch_args_attr:
                if attr.data_type == "string":
                    layout.row().prop(attr, "string_value", text=attr.description if attr.description else attr.name)
                elif attr.data_type == "float":
                    layout.row().prop(attr, "float_value", text=attr.description if attr.description else attr.name)
                elif attr.data_type == "boolean":
                    layout.row().prop(attr, "bool_value", text=attr.description if attr.description else attr.name)
                elif attr.data_type == "integer":
                    layout.row().prop(attr, "int_value", text=attr.description if attr.description else attr.name)
        else:
            row = layout.row()
            row.prop(props, "ifc_patch_args")

        row = layout.row()
        op = row.operator("bim.execute_ifc_patch")
