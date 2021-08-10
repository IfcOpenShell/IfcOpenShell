import blenderbim.bim.helper
from bpy.types import Panel
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.style.data import Data


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
        material = context.active_object.active_material
        props = material.BIMMaterialProperties
        row = self.layout.row(align=True)
        if props.ifc_style_id:
            row.operator("bim.update_style_colours", icon="GREASEPENCIL").material = material.name
            row.operator("bim.unlink_style", icon="UNLINKED", text="").material = material.name
            row.operator("bim.remove_style", icon="X", text="").material = material.name
        else:
            row.operator("bim.add_style", icon="ADD")


class BIM_PT_style_attributes(Panel):
    bl_label = "IFC Style Attributes"
    bl_idname = "BIM_PT_style_attributes"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"

    @classmethod
    def poll(cls, context):
        try:
            return bool(context.active_object.active_material.BIMMaterialProperties.ifc_style_id)
        except:
            return False

    def draw(self, context):
        obj = context.active_object.active_material
        mprops = obj.BIMMaterialProperties
        props = obj.BIMStyleProperties
        if mprops.ifc_style_id not in Data.styles:
            Data.load(IfcStore.get_file(), mprops.ifc_style_id)
        if props.is_editing_attributes:
            row = self.layout.row(align=True)
            row.operator("bim.edit_style", icon="CHECKMARK")
            row.operator("bim.disable_editing_style", icon="CANCEL", text="")
            blenderbim.bim.helper.draw_attributes(props.attributes, self.layout)
        else:
            row = self.layout.row()
            row.operator("bim.enable_editing_style", icon="GREASEPENCIL", text="Edit")

            row = self.layout.row(align=True)
            row.label(text="STEP ID")
            row.label(text=str(mprops.ifc_style_id))

            for name, value in Data.styles[mprops.ifc_style_id].items():
                if name in ["id", "type", "Styles"]:
                    continue
                row = self.layout.row(align=True)
                row.label(text=name)
                row.label(text=str(value))
