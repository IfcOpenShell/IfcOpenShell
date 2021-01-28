from bpy.types import Panel
from blenderbim.bim.module.type.data import Data


class BIM_PT_type(Panel):
    bl_label = "IFC Construction Type"
    bl_idname = "BIM_PT_type"
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

        if props.is_editing_type:
            row = self.layout.row(align=True)
            row.prop(props, "relating_type", text="")
            row.operator("bim.assign_type", icon="CHECKMARK", text="")
            row.operator("bim.disable_editing_type", icon="X", text="")
        else:
            row = self.layout.row(align=True)
            name = "{}/{}".format(
                Data.products[props.ifc_definition_id]["type"], Data.products[props.ifc_definition_id]["Name"]
            )
            if name == "None/None":
                label = "This object has no type"
            else:
                label = name
            row.label(text=label)
            row.operator("bim.select_similar_type", icon="RESTRICT_SELECT_OFF", text="")
            row.operator("bim.enable_editing_type", icon="GREASEPENCIL", text="")
            if name != "None/None":
                row.operator("bim.unassign_type", icon="X", text="")
