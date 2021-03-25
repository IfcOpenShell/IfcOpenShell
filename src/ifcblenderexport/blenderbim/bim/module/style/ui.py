from bpy.types import Panel
from blenderbim.bim.ifc import IfcStore


class BIM_PT_style(Panel):
    bl_label = "IFC Style"
    bl_idname = "BIM_PT_style"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        return (
            IfcStore.get_file()
            and context.active_object is not None
            and context.active_object.active_material is not None
        )

    def draw(self, context):
        props = context.active_object.active_material.BIMMaterialProperties
        row = self.layout.row(align=True)
        if props.ifc_style_id:
            row.operator("bim.edit_style", icon="GREASEPENCIL")
            op = row.operator("bim.unlink_style", icon="UNLINKED", text="")
            op.material = context.active_object.active_material.name
        else:
            row.operator("bim.add_style", icon="ADD")
