import bpy
from bpy.types import Panel
from ifcopenshell.api.root.data import Data
from blenderbim.bim.ifc import IfcStore


class BIM_PT_class(Panel):
    bl_label = "IFC Class"
    bl_idname = "BIM_PT_class"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        props = context.active_object.BIMObjectProperties
        if props.ifc_definition_id:
            if props.ifc_definition_id not in Data.products:
                try:
                    Data.load(IfcStore.get_file(), props.ifc_definition_id)
                except:
                    row = self.layout.row(align=True)
                    row.label(text="IFC Element Not Found")
                    row.operator("bim.unlink_object", icon="UNLINKED", text="")
                    return
            if props.is_reassigning_class:
                row = self.layout.row(align=True)
                row.operator("bim.reassign_class", icon="CHECKMARK")
                row.operator("bim.disable_reassign_class", icon="X", text="")
                self.draw_class_dropdowns(context)
            else:
                data = Data.products[props.ifc_definition_id]
                name = data["type"]
                if data["PredefinedType"] and data["PredefinedType"] == "USERDEFINED":
                    name += "[{}]".format(data["ObjectType"])
                elif data["PredefinedType"]:
                    name += "[{}]".format(data["PredefinedType"])
                row = self.layout.row(align=True)
                row.label(text=name)
                row.operator("bim.select_ifc_class", text="", icon="RESTRICT_SELECT_OFF").ifc_class = data["type"]
                row.operator("bim.copy_class", icon="DUPLICATE", text="")
                row.operator("bim.unlink_object", icon="UNLINKED", text="")
                if IfcStore.get_file().by_id(props.ifc_definition_id).is_a("IfcRoot"):
                    row.operator("bim.enable_reassign_class", icon="GREASEPENCIL", text="")
                if context.selected_objects:
                    row.operator("bim.unassign_class", icon="X", text="")
                else:
                    row.operator("bim.unassign_class", icon="X", text="").obj = context.active_object.name
        else:
            self.draw_class_dropdowns(context)
            row = self.layout.row(align=True)
            op = row.operator("bim.assign_class")
            op.ifc_class = context.scene.BIMRootProperties.ifc_class
            op.predefined_type = context.scene.BIMRootProperties.ifc_predefined_type
            op.userdefined_type = context.scene.BIMRootProperties.ifc_userdefined_type

    def draw_class_dropdowns(self, context):
        props = context.scene.BIMRootProperties
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
        row = self.layout.row()
        row.prop(context.scene.BIMProperties, "contexts")
