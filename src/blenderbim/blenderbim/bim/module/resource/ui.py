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
        self.props = context.scene.BIMResourceProperties
        self.tprops = context.scene.BIMResourceTreeProperties
        row = self.layout.row()
        if self.props.is_loaded:
            row.operator("bim.disable_resource_editing_ui", text="CANCEL EDITING RESOURCES", icon="CANCEL")
        else:
            row.operator("bim.load_resources", text="Load Resources", icon="GREASEPENCIL")

        if not Data.is_loaded:
            Data.load(IfcStore.get_file())
        if self.props.is_loaded:
            row = self.layout.row(align=True)
            row.operator("bim.add_subcontract_resource", text="Add Subcontract", icon="FILE_TICK")
            row.operator("bim.add_crew_resource", text="Add Crew", icon="COMMUNITY")
            for resource_id, resource in Data.resources.items():
                self.draw_resource_ui(resource_id, resource)

    def draw_resource_ui(self, resource_id, resource):
        row = self.layout.row()
        row.label(text=resource["Name"] or "Unnamed", icon="BOOKMARKS")
        if self.props.active_resource_id and self.props.active_resource_id == resource_id:
            if self.props.is_editing == "RESOURCE":
                row.operator("bim.edit_resource", text="", icon="CHECKMARK")
            elif self.props.is_editing == "NESTED_RESOURCE":
                row.operator("bim.add_subcontract_resource", text="", icon="FILE_TICK").resource = resource_id
                row.operator("bim.add_crew_resource", text="", icon="COMMUNITY").resource = resource_id
                row.operator("bim.add_equipment_resource", text="", icon="TOOL_SETTINGS").resource = resource_id
                row.operator("bim.add_labor_resource", text="", icon="ARMATURE_DATA").resource = resource_id
                row.operator("bim.add_material_resource", text="", icon="MATERIAL").resource = resource_id
                row.operator("bim.add_product_resource", text="", icon="PACKAGE").resource = resource_id
                row.operator("bim.edit_resource", text="", icon="CHECKMARK")#.resource = resource_id
                #TODO add if statement in operator for editing resource so that it doesnt toggle the wrong panel
            row.operator("bim.disable_editing_resource", text="", icon="CANCEL")
        elif self.props.active_resource_id:
            row.operator("bim.remove_resource", text="", icon="X").resource = resource_id
        else:
            row.operator("bim.enable_editing_nested_resources", text="", icon="ACTION").resource = resource_id
            row.operator("bim.enable_editing_resource", text="", icon="GREASEPENCIL").resource = resource_id

        if self.props.active_resource_id == resource_id:
            if self.props.is_editing == "RESOURCE":
                self.draw_editable_resource_ui()
            elif self.props.is_editing == "NESTED_RESOURCE":
                self.draw_editable_nested_resource_ui(resource_id)

    def draw_editable_resource_ui(self):
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

    def draw_editable_nested_resource_ui(self, resource_id):
        self.layout.template_list(
            "BIM_UL_nested_resources",
            "",
            self.tprops,
            "nested_resources",
            self.props,
            "active_nested_resource_index",
        )
        if self.props.active_nested_resource_id:
            self.draw_editable_nested_resource_attributes_ui()


    def draw_editable_nested_resource_attributes_ui(self):
        for attribute in self.props.nested_resource_attributes:
            row = self.layout.row(align=True)
            if attribute.data_type == "string":
                row.prop(attribute, "string_value", text=attribute.name)
            elif attribute.data_type == "boolean":
                row.prop(attribute, "bool_value", text=attribute.name)
            elif attribute.data_type == "integer":
                row.prop(attribute, "int_value", text=attribute.name)
            elif attribute.data_type == "enum":
                row.prop(attribute, "enum_value", text=attribute.name)
            if attribute.is_optional:
                row.prop(attribute, "is_null", icon="RADIOBUT_OFF" if attribute.is_null else "RADIOBUT_ON", text="")


class BIM_UL_nested_resources(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            props = context.scene.BIMResourceProperties
            row = layout.row(align=True)
            for i in range(0, item.level_index):
                row.label(text="", icon="BLANK1")
            if item.has_children:
                if item.is_expanded:
                    row.operator(
                        "bim.contract_nested_resource", text="", emboss=False, icon="DISCLOSURE_TRI_DOWN"
                    ).nested_resource = item.ifc_definition_id
                else:
                    row.operator(
                        "bim.expand_nested_resource", text="", emboss=False, icon="DISCLOSURE_TRI_RIGHT"
                    ).nested_resource = item.ifc_definition_id

            if props.active_nested_resource_id == item.ifc_definition_id:
                row.operator("bim.edit_nested_resource", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_nested_resource", text="", icon="CANCEL")
            elif props.active_nested_resource_id:
                row.operator("bim.add_nested_resource", text="", icon="ADD").nested_resource = item.ifc_definition_id
                row.operator("bim.remove_nested_resource", text="", icon="X").nested_resource = item.ifc_definition_id
            else:
                row.operator("bim.enable_editing_nested_resource_time", text="", icon="TIME").nested_resource = item.ifc_definition_id
                row.operator("bim.enable_editing_nested_resource", text="", icon="GREASEPENCIL").nested_resource = item.ifc_definition_id
                row.operator("bim.add_nested_resource", text="", icon="ADD").nested_resource = item.ifc_definition_id
                row.operator("bim.remove_nested_resource", text="", icon="X").nested_resource = item.ifc_definition_id
