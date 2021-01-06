from bpy.types import Panel


class BIM_PT_style(Panel):
    bl_label = "IFC Style"
    bl_idname = "BIM_PT_style"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.active_material is not None

    def draw(self, context):
        props = context.active_object.active_material.BIMMaterialProperties
        row = self.layout.row()
        if props.ifc_style_id:
            row.operator("bim.edit_style", icon="GREASEPENCIL")
        else:
            row.operator("bim.add_style", icon="ADD")
