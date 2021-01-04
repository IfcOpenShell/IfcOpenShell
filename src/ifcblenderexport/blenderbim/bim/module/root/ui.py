import bpy
from bpy.types import Panel
from blenderbim.bim.module.root.data import Data

class BIM_PT_class(Panel):
    bl_label = "IFC Class"
    bl_idname = "BIM_PT_class"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    def draw(self, context):
        props = context.active_object.BIMObjectProperties
        if props.ifc_definition_id:
            if props.ifc_definition_id not in Data.products:
                Data.load(props.ifc_definition_id)
            if props.is_reassigning_class:
                self.draw_class_dropdowns()
                row = self.layout.row(align=True)
                row.operator("bim.reassign_class", icon="CHECKMARK")
                row.operator("bim.disable_reassign_class", icon="X", text="")
            else:
                data = Data.products[props.ifc_definition_id]
                name = data["type"]
                if data["PredefinedType"] and data["PredefinedType"] == "USERDEFINED":
                    name += "[{}]".format(data["ObjectType"])
                elif data["PredefinedType"]:
                    name += "[{}]".format(data["PredefinedType"])
                row = self.layout.row(align=True)
                row.label(text=name)
                row.operator("bim.enable_reassign_class", icon="GREASEPENCIL", text="")
                op = row.operator("bim.unassign_class", icon="X", text="")
                op.object_name = context.active_object.name
        else:
            self.draw_class_dropdowns()
            row = self.layout.row(align=True)
            op = row.operator("bim.assign_class")
            op.object_name = context.active_object.name

    def draw_class_dropdowns(self):
        props = bpy.context.scene.BIMProperties
        row = self.layout.row()
        row.prop(props, "ifc_product")
        row = self.layout.row()
        row.prop(props, "ifc_class")
        if props.ifc_predefined_type:
            row = self.layout.row()
            row.prop(props, "ifc_predefined_type")
        if props.ifc_predefined_type == "USERDEFINED":
            row = self.layout.row()
            row.prop(props, "ifc_userdefined_type")
