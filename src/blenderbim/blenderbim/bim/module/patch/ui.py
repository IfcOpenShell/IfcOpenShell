import bpy
from blenderbim.bim.helper import draw_attributes


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
        

        row = layout.row(align=True)
        row.prop(props, "ifc_patch_input")
        row.operator("bim.select_ifc_patch_input", icon="FILE_FOLDER", text="")

        row = layout.row(align=True)
        row.prop(props, "ifc_patch_output")
        row.operator("bim.select_ifc_patch_output", icon="FILE_FOLDER", text="")

        if props.ifc_patch_args_attr:
            draw_attributes(props.ifc_patch_args_attr, layout)
        else:
            layout.row().prop(props, "ifc_patch_args")
        op = layout.operator("bim.execute_ifc_patch")
        op.use_json_for_args = len(props.ifc_patch_args_attr) == 0
