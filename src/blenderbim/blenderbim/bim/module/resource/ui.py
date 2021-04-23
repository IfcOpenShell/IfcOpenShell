from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.resource.data import Data

class BIM_PT_resources(Panel):
    bl_label = "IFC Resources"
    bl_idname = "BIM_PT_resources"
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
        self.props = context.scene.BIMResourceProperties

        row = self.layout.row(align=True)
        if self.props.is_editing:
            row.operator("bim.add_subcontract_resource",emboss=False, text="", icon="FILE_TICK")
            row.operator("bim.add_crew_resource",emboss=False, text="", icon="COMMUNITY")
            row.operator("bim.disable_resource_editing_ui", text="", icon="CANCEL")
        else:
            row.operator("bim.load_resources", text="", icon="GREASEPENCIL")

        if self.props.is_editing:
            self.layout.template_list(
                "BIM_UL_resources",
                "",
                self.props,
                "resources",
                self.props,
                "active_resource_index",
            )

        if self.props.active_resource_id:
            self.draw_editable_ui(context)

    def draw_editable_ui(self, context):
        for attribute in self.props.resource_attributes:
            row = self.layout.row(align=True)
            if attribute.data_type == "string":
                row.prop(attribute, "string_value", text=attribute.name)
            elif attribute.data_type == "boolean":
                row.prop(attribute, "bool_value", text=attribute.name)
            elif attribute.data_type == "integer":
                row.prop(attribute, "int_value", text=attribute.name)
            elif attribute.data_type == "float":
                row.prop(attribute, "float_value", text=attribute.name)
            elif attribute.data_type == "enum":
                row.prop(attribute, "enum_value", text=attribute.name)
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")


class BIM_UL_resources(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            row.label(text=item.name)
            if context.scene.BIMResourceProperties.active_resource_id == item.ifc_definition_id:
                row.operator("bim.edit_resource", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_resource", text="", icon="X")
            elif context.scene.BIMResourceProperties.active_resource_id:
                row.operator("bim.remove_resource", text="", icon="X").resource = item.ifc_definition_id
            else:
                op = row.operator("bim.enable_editing_resource", text="", icon="GREASEPENCIL")
                op.resource = item.ifc_definition_id
                row.operator("bim.remove_resource", text="", icon="X").resource = item.ifc_definition_id
