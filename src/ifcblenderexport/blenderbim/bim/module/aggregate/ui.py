from bpy.types import Panel
from blenderbim.bim.module.aggregate.data import Data


class BIM_PT_aggregate(Panel):
    bl_label = "IFC Aggregation"
    bl_idname = "BIM_PT_aggregate"
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

        if props.is_editing_aggregate:
            row = self.layout.row(align=True)
            row.prop(props, "relating_object", text="")
            row.operator("bim.assign_object", icon="CHECKMARK", text="")
            row.operator("bim.disable_editing_aggregate", icon="X", text="")
        else:
            row = self.layout.row(align=True)
            name = "{}/{}".format(
                Data.products[props.ifc_definition_id]["type"], Data.products[props.ifc_definition_id]["Name"]
            )
            if name == "None/None":
                name = "This object is not part of an aggregation"
            row.label(text=name)
            row.operator("bim.enable_editing_aggregate", icon="GREASEPENCIL", text="")
