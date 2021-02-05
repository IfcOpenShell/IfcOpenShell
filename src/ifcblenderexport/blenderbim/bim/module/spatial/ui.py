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
        if not context.active_object:
            return False
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

        if props.is_editing_container:
            row = self.layout.row(align=True)
            row.prop(props, "relating_structure", text="")
            row.operator("bim.assign_container", icon="CHECKMARK", text="")
            row.operator("bim.disable_editing_container", icon="X", text="")
        else:
            row = self.layout.row(align=True)
            name = "{}/{}".format(
                Data.products[props.ifc_definition_id]["type"], Data.products[props.ifc_definition_id]["Name"]
            )
            if name == "None/None":
                name = "This object is not spatially contained"
            row.label(text=name)
            row.operator("bim.enable_editing_container", icon="GREASEPENCIL", text="")
            row.operator("bim.remove_container", icon="X", text="")
