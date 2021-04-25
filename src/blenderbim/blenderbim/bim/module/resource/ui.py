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

        if not Data.is_loaded:
            Data.load(IfcStore.get_file())

        row = self.layout.row(align=True)
        row.label(text=f"{len(Data.resources)} Resources Found")
        if self.props.is_editing:
            row.operator("bim.disable_resource_editing_ui", text="", icon="CANCEL")
        else:
            row.operator("bim.load_resources", text="", icon="GREASEPENCIL")

        if not self.props.is_editing:
            return

        row = self.layout.row(align=True)
        op = row.operator("bim.add_resource", text="Add SubContract", icon="TEXT")
        op.ifc_class = "IfcSubContractResource"
        op.resource = 0
        op = row.operator("bim.add_resource", text="Add Crew", icon="COMMUNITY")
        op.ifc_class = "IfcCrewResource"
        op.resource = 0

        icon_map = {
            "IfcConstructionEquipmentResource": "TOOL_SETTINGS",
            "IfcLaborResource": "OUTLINER_OB_ARMATURE",
            "IfcConstructionMaterialResource": "MATERIAL",
            "IfcConstructionProductResource": "PACKAGE",
        }

        total_resources = len(self.tprops.resources)
        if total_resources and self.props.active_resource_index < total_resources:
            row = self.layout.row(align=True)
            for ifc_class, icon in icon_map.items():
                label = ifc_class.replace("Ifc", "").replace("Construction", "").replace("Resource", "")
                op = row.operator("bim.add_resource", text=label, icon=icon)
                op.resource = self.tprops.resources[self.props.active_resource_index].ifc_definition_id
                op.ifc_class = ifc_class

        self.layout.template_list(
            "BIM_UL_resources",
            "",
            self.tprops,
            "resources",
            self.props,
            "active_resource_index",
        )
        if self.props.active_resource_id:
            self.draw_editable_resource_ui()

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


class BIM_UL_resources(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        resource = Data.resources[item.ifc_definition_id]
        icon_map = {
            "IfcSubContractResource": "TEXT",
            "IfcCrewResource": "COMMUNITY",
            "IfcConstructionEquipmentResource": "TOOL_SETTINGS",
            "IfcLaborResource": "OUTLINER_OB_ARMATURE",
            "IfcConstructionMaterialResource": "MATERIAL",
            "IfcConstructionProductResource": "PACKAGE",
        }
        if item:
            props = context.scene.BIMResourceProperties
            row = layout.row(align=True)
            for i in range(0, item.level_index):
                row.label(text="", icon="BLANK1")
            if item.has_children:
                if item.is_expanded:
                    row.operator(
                        "bim.contract_resource", text="", emboss=False, icon="DISCLOSURE_TRI_DOWN"
                    ).resource = item.ifc_definition_id
                else:
                    row.operator(
                        "bim.expand_resource", text="", emboss=False, icon="DISCLOSURE_TRI_RIGHT"
                    ).resource = item.ifc_definition_id
            else:
                row.label(text="", icon="DOT")
            row.prop(item, "name", emboss=False, text="", icon=icon_map[resource["type"]])

            if context.active_object:
                oprops = context.active_object.BIMObjectProperties
                row = layout.row(align=True)
                if oprops.ifc_definition_id in Data.resources[item.ifc_definition_id]["RelatedObjects"]:
                    op = row.operator("bim.unassign_resource", text="", icon="KEYFRAME_HLT", emboss=False)
                    op.resource = item.ifc_definition_id
                else:
                    op = row.operator("bim.assign_resource", text="", icon="KEYFRAME", emboss=False)
                    op.resource = item.ifc_definition_id

            if props.active_resource_id == item.ifc_definition_id:
                row.operator("bim.edit_resource", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_resource", text="", icon="CANCEL")
            elif props.active_resource_id:
                row.operator("bim.add_resource", text="", icon="ADD").resource = item.ifc_definition_id
                row.operator("bim.remove_resource", text="", icon="X").resource = item.ifc_definition_id
            else:
                row.operator(
                    "bim.enable_editing_resource", text="", icon="GREASEPENCIL"
                ).resource = item.ifc_definition_id

                row.operator("bim.remove_resource", text="", icon="X").resource = item.ifc_definition_id
