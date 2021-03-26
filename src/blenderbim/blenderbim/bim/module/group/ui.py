from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.group.data import Data


class BIM_PT_groups(Panel):
    bl_label = "IFC Groups"
    bl_idname = "BIM_PT_groups"
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
        self.props = context.scene.BIMGroupProperties

        row = self.layout.row(align=True)
        row.label(text="{} Groups Found".format(len(Data.groups)), icon="OUTLINER")
        if self.props.is_editing:
            row.operator("bim.add_group", text="", icon="ADD")
            row.operator("bim.disable_group_editing_ui", text="", icon="CHECKMARK")
        else:
            row.operator("bim.load_groups", text="", icon="GREASEPENCIL")

        if self.props.is_editing:
            self.layout.template_list(
                "BIM_UL_groups",
                "",
                self.props,
                "groups",
                self.props,
                "active_group_index",
            )

        if self.props.active_group_id:
            self.draw_editable_ui(context)

    def draw_editable_ui(self, context):
        for attribute in self.props.group_attributes:
            row = self.layout.row(align=True)
            row.prop(attribute, "string_value", text=attribute.name)
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")



class BIM_UL_groups(UIList):
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
                    op = row.operator("bim.unassign_group", text="", icon="KEYFRAME_HLT", emboss=False)
                    op.group = item.ifc_definition_id
                else:
                    op = row.operator("bim.assign_group", text="", icon="KEYFRAME", emboss=False)
                    op.group = item.ifc_definition_id

            if context.scene.BIMGroupProperties.active_group_id == item.ifc_definition_id:
                row.operator("bim.edit_group", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_group", text="", icon="X")
            elif context.scene.BIMGroupProperties.active_group_id:
                row.operator("bim.remove_group", text="", icon="X").group = item.ifc_definition_id
            else:
                op = row.operator("bim.enable_editing_group", text="", icon="GREASEPENCIL")
                op.group = item.ifc_definition_id
                row.operator("bim.remove_group", text="", icon="X").group = item.ifc_definition_id
