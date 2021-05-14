import bpy
from bpy.types import Panel


class BIM_PT_patch(Panel):
    bl_label = "IFC Patch"
    bl_idname = "BIM_PT_patch"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

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
        row = layout.row()
        row.prop(props, "ifc_patch_args")

        row = layout.row()
        op = row.operator("bim.execute_ifc_patch")
