from bpy.types import Panel
from blenderbim.bim.module.spatial.data import Data


class BIM_PT_spatial(Panel):
    bl_label = "IFC Spatial Container"
    bl_idname = "BIM_PT_spatial"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        props = context.active_object.BIMObjectProperties
        if not props.ifc_definition_id:
            return False
        if props.ifc_definition_id not in Data.products:
            Data.load(props.ifc_definition_id)
        if not Data.products[props.ifc_definition_id]:
            return False
        return True

    def draw(self, context):
        props = context.active_object.BIMObjectProperties
        if not props.ifc_definition_id:
            return
        if props.ifc_definition_id not in Data.products:
            Data.load(props.ifc_definition_id)

        row = self.layout.row(align=True)
        name = "{}/{}".format(
            Data.products[props.ifc_definition_id]["type"], Data.products[props.ifc_definition_id]["Name"]
        )
        row.label(text=name)
        row.operator("bim.assign_container", icon="FILE_REFRESH", text="")
