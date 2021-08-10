from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.system.data import Data


class BIM_PT_systems(Panel):
    bl_label = "IFC Systems"
    bl_idname = "BIM_PT_systems"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        return IfcStore.get_file()

    def draw(self, context):
        if not Data.is_loaded:
            Data.load(IfcStore.get_file())
        self.props = context.scene.BIMSystemProperties

        row = self.layout.row(align=True)
        row.label(text="{} Systems Found".format(len(Data.systems)), icon="OUTLINER")
        if self.props.is_editing:
            row.operator("bim.add_system", text="", icon="ADD")
            row.operator("bim.disable_system_editing_ui", text="", icon="CANCEL")
        else:
            row.operator("bim.load_systems", text="", icon="GREASEPENCIL")

        if self.props.is_editing:
            self.layout.template_list(
                "BIM_UL_systems",
                "",
                self.props,
                "systems",
                self.props,
                "active_system_index",
            )

        if self.props.active_system_id:
            self.draw_editable_ui(context)

    def draw_editable_ui(self, context):
        for attribute in self.props.system_attributes:
            row = self.layout.row(align=True)
            row.prop(attribute, "string_value", text=attribute.name)
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")



class BIM_UL_systems(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.label(text=item.name)

            if context.active_object:
                oprops = context.active_object.BIMObjectProperties
                if (
                    oprops.ifc_definition_id in Data.products
                    and item.ifc_definition_id in Data.products[oprops.ifc_definition_id]
                ):
                    op = row.operator("bim.unassign_system", text="", icon="KEYFRAME_HLT", emboss=False)
                    op.system = item.ifc_definition_id
                else:
                    op = row.operator("bim.assign_system", text="", icon="KEYFRAME", emboss=False)
                    op.system = item.ifc_definition_id

            if context.scene.BIMSystemProperties.active_system_id == item.ifc_definition_id:
                op = row.operator("bim.select_system_products", text="", icon="RESTRICT_SELECT_OFF")
                op.system = item.ifc_definition_id
                row.operator("bim.edit_system", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_system", text="", icon="CANCEL")
            elif context.scene.BIMSystemProperties.active_system_id:
                op = row.operator("bim.select_system_products", text="", icon="RESTRICT_SELECT_OFF")
                op.system = item.ifc_definition_id
                row.operator("bim.remove_system", text="", icon="X").system = item.ifc_definition_id
            else:
                op = row.operator("bim.select_system_products", text="", icon="RESTRICT_SELECT_OFF")
                op.system = item.ifc_definition_id
                op = row.operator("bim.enable_editing_system", text="", icon="GREASEPENCIL")
                op.system = item.ifc_definition_id
                row.operator("bim.remove_system", text="", icon="X").system = item.ifc_definition_id
