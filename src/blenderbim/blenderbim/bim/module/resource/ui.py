# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import blenderbim.bim.helper
from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.module.resource.data import ResourceData


class BIM_PT_resources(Panel):
    bl_label = "Resources"
    bl_idname = "BIM_PT_resources"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_4D5D"

    @classmethod
    def poll(cls, context):
        file = IfcStore.get_file()
        return file and hasattr(file, "schema") and file.schema != "IFC2X3"

    def draw(self, context):
        self.props = context.scene.BIMResourceProperties
        self.tprops = context.scene.BIMResourceTreeProperties
        if not ResourceData.is_loaded:
            ResourceData.load()

        row = self.layout.row(align=True)
        if ResourceData.data["total_resources"]:
            row.label(text=f"{ResourceData.data['total_resources']} Resources Found", icon="TEXT")
        else:
            row.label(text="No Resources found.", icon="COMMUNITY")
        if self.props.is_editing:
            row.operator("bim.disable_resource_editing_ui", text="", icon="CANCEL")
        else:
            row.operator("bim.load_resources", text="", icon="GREASEPENCIL")
            row.operator("import_resources.bim", text="", icon="IMPORT")
        if not self.props.is_editing:
            return

        self.draw_resource_operators()

        self.layout.template_list(
            "BIM_UL_resources",
            "",
            self.tprops,
            "resources",
            self.props,
            "active_resource_index",
        )
        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        row.prop(self.props, "should_show_productivity", icon="RECOVER_LAST")
        if self.props.should_show_productivity:
            self.draw_productivity_ui(context)
        if self.props.active_resource_id and self.props.editing_resource_type == "ATTRIBUTES":
            self.draw_editable_resource_attributes_ui()
        elif self.props.active_resource_id and self.props.editing_resource_type == "QUANTITY":
            self.draw_editable_resource_quantity_ui()
        elif self.props.active_resource_id and self.props.editing_resource_type == "COSTS":
            self.draw_editable_resource_costs_ui()
        elif self.props.active_resource_id and self.props.editing_resource_type == "USAGE":
            self.draw_editable_resource_time_attributes_ui()

    def draw_productivity_ui(self, context):
        total_resources = len(self.tprops.resources)
        if not total_resources or self.props.active_resource_index >= total_resources:
            return

        ifc_definition_id = self.tprops.resources[self.props.active_resource_index].ifc_definition_id
        resource = ResourceData.data["resources"][ifc_definition_id]

        if not resource["type"] in ["IfcConstructionEquipmentResource", "IfcLaborResource"]:
            row = self.layout.row(align=True)
            row.label(text="Resource type cannot have productivity data", icon="ERROR")
            return

        self.productivity_props = context.scene.BIMResourceProductivity

        if resource["Productivity"]:
            produtivitiy_rate_message = "Current Rate: {}/{}".format(
                resource["Productivity"]["QuantityProduced"], resource["Productivity"]["TimeConsumed"]
            )
            row = self.layout.row()
            row.alignment = "LEFT"
            row.label(text=produtivitiy_rate_message, icon="ARMATURE_DATA")
        else:
            row = self.layout.row(align=True)
            row.alignment = "LEFT"
            produtivitiy_rate_message = "No productivity data found"
            row.label(text=produtivitiy_rate_message, icon="ARMATURE_DATA")

        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        row.prop(self.productivity_props, "quantity_produced", text="Quantity Produced")
        row.prop(self.productivity_props, "quantity_produced_name", text="Quantity Name")
        row = self.layout.row()
        row.alignment = "RIGHT"
        self.draw_duration_property(self.productivity_props.quantity_consumed, row)
        row = self.layout.row()
        row.alignment = "RIGHT"
        row.operator("bim.edit_productivity_data", text="Apply", icon="CHECKMARK")

    def draw_resource_operators(self):
        row = self.layout.row(align=True)
        op = row.operator("bim.add_resource", text="Add SubContract", icon="TEXT")
        op.ifc_class = "IfcSubContractResource"
        op.parent_resource = 0
        op = row.operator("bim.add_resource", text="Add Crew", icon="COMMUNITY")
        op.ifc_class = "IfcCrewResource"
        op.parent_resource = 0

        total_resources = len(self.tprops.resources)
        if not total_resources or self.props.active_resource_index >= total_resources:
            return

        ifc_definition_id = self.tprops.resources[self.props.active_resource_index].ifc_definition_id
        resource = ResourceData.data["resources"][ifc_definition_id]

        if resource["type"] != "IfcSubContractResource":
            icon_map = {
                "IfcSubContractResource": "TEXT",
                "IfcConstructionEquipmentResource": "TOOL_SETTINGS",
                "IfcLaborResource": "OUTLINER_OB_ARMATURE",
                "IfcConstructionMaterialResource": "MATERIAL",
                "IfcConstructionProductResource": "PACKAGE",
            }
            row = self.layout.row(align=True)
            for ifc_class, icon in icon_map.items():
                label = ifc_class.replace("Ifc", "").replace("Construction", "").replace("Resource", "")
                op = row.operator("bim.add_resource", text=label, icon=icon)
                op.parent_resource = ifc_definition_id
                op.ifc_class = ifc_class

        row = self.layout.row(align=True)
        row.alignment = "RIGHT"

        if not self.props.active_resource_id:
            if resource["type"] in ["IfcLaborResource", "IfcConstructionEquipmentResource"]:
                if resource["Productivity"]:
                    op = row.operator("bim.calculate_resource_work", text="", icon="TEMP")
                    op.resource = ifc_definition_id
                row.operator("bim.enable_editing_resource_time", text="", icon="TIME").resource = ifc_definition_id
            op = row.operator("bim.enable_editing_resource_base_quantity", text="", icon="PROPERTIES")
            op.resource = ifc_definition_id
            op = row.operator("bim.enable_editing_resource_costs", text="", icon="DISC")
            op.resource = ifc_definition_id
            row.operator("bim.enable_editing_resource", text="", icon="GREASEPENCIL").resource = ifc_definition_id
            row.operator("bim.remove_resource", text="", icon="X").resource = ifc_definition_id

    def draw_editable_resource_attributes_ui(self):
        blenderbim.bim.helper.draw_attributes(self.props.resource_attributes, self.layout)

    def draw_editable_resource_time_attributes_ui(self):
        blenderbim.bim.helper.draw_attributes(self.props.resource_time_attributes, self.layout)

    def draw_editable_resource_quantity_ui(self):
        resource = ResourceData.data["resources"][self.props.active_resource_id]

        if resource["BaseQuantity"]:
            quantity = resource["BaseQuantity"]
            value = quantity[[k for k in quantity.keys() if "Value" in k][0]]
            row = self.layout.row(align=True)
            row.label(text=quantity["Name"])
            row.label(text="{0:.2f}".format(value))
            if self.props.is_editing_quantity:
                op = row.operator("bim.edit_resource_quantity", text="", icon="CHECKMARK")
                op.physical_quantity = quantity["id"]
                row.operator("bim.disable_editing_resource_quantity", text="", icon="CANCEL")
            else:
                op = row.operator("bim.enable_editing_resource_quantity", text="", icon="GREASEPENCIL")
                op.resource = self.props.active_resource_id
                op = row.operator("bim.remove_resource_quantity", text="", icon="X")
                op.resource = self.props.active_resource_id

            if self.props.is_editing_quantity:
                box = self.layout.box()
                blenderbim.bim.helper.draw_attributes(self.props.quantity_attributes, box)
        else:
            row = self.layout.row(align=True)
            row.prop(self.props, "quantity_types", text="")
            op = row.operator("bim.add_resource_quantity", text="", icon="ADD")
            op.resource = self.props.active_resource_id
            op.ifc_class = self.props.quantity_types

    def draw_editable_resource_costs_ui(self):
        row = self.layout.row(align=True)
        row.prop(self.props, "cost_types", text="")
        if self.props.cost_types == "CATEGORY":
            row.prop(self.props, "cost_category", text="")
        op = row.operator("bim.add_cost_value", text="", icon="ADD")
        op.parent = self.props.active_resource_id
        op.cost_type = self.props.cost_types
        if self.props.cost_types == "CATEGORY":
            op.cost_category = self.props.cost_category

        for cost_value in ResourceData.data["cost_values"]:
            row = self.layout.row(align=True)
            self.draw_readonly_cost_value_ui(row, cost_value)

        if self.props.cost_value_editing_type == "ATTRIBUTES":
            blenderbim.bim.helper.draw_attributes(self.props.cost_value_attributes, self.layout.box())

    def draw_readonly_cost_value_ui(self, layout, cost_value):
        if self.props.active_cost_value_id == cost_value["id"] and self.props.cost_value_editing_type == "FORMULA":
            layout.prop(self.props, "cost_value_formula", text="")
        else:
            layout.label(text=cost_value["label"], icon="DISC")

        self.draw_cost_value_operator_ui(layout, cost_value["id"], self.props.active_resource_id)

    def draw_cost_value_operator_ui(self, layout, cost_value_id, parent_id):
        if self.props.active_cost_value_id and self.props.active_cost_value_id == cost_value_id:
            if self.props.cost_value_editing_type == "ATTRIBUTES":
                op = layout.operator("bim.edit_resource_cost_value", text="", icon="CHECKMARK")
                op.cost_value = cost_value_id
            elif self.props.cost_value_editing_type == "FORMULA":
                op = layout.operator("bim.edit_resource_cost_value_formula", text="", icon="CHECKMARK")
                op.cost_value = cost_value_id
            layout.operator("bim.disable_editing_resource_cost_value", text="", icon="CANCEL")
        elif self.props.active_cost_value_id:
            op = layout.operator("bim.remove_cost_value", text="", icon="X")
            op.parent = parent_id
            op.cost_value = cost_value_id
        else:
            op = layout.operator("bim.enable_editing_resource_cost_value_formula", text="", icon="CON_TRANSLIKE")
            op.cost_value = cost_value_id
            op = layout.operator("bim.enable_editing_resource_cost_value", text="", icon="GREASEPENCIL")
            op.cost_value = cost_value_id
            op = layout.operator("bim.remove_cost_value", text="", icon="X")
            op.parent = parent_id
            op.cost_value = cost_value_id

    def draw_duration_property(self, duration_props, layout):
        for duration_prop in duration_props:
            if duration_prop.name == "BaseQuantityConsumed":
                layout.label(text=duration_prop.name)
                layout.prop(duration_prop, "years", text="Y")
                layout.prop(duration_prop, "months", text="M")
                layout.prop(duration_prop, "days", text="D")
                layout.prop(duration_prop, "hours", text="H")
                layout.prop(duration_prop, "minutes", text="Min")
                layout.prop(duration_prop, "seconds", text="S")


class BIM_UL_resources(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        icon_map = {
            "IfcSubContractResource": "TEXT",
            "IfcCrewResource": "COMMUNITY",
            "IfcConstructionEquipmentResource": "TOOL_SETTINGS",
            "IfcLaborResource": "OUTLINER_OB_ARMATURE",
            "IfcConstructionMaterialResource": "MATERIAL",
            "IfcConstructionProductResource": "PACKAGE",
        }
        if item:
            resource = ResourceData.data["resources"][item.ifc_definition_id]
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
            row.prop(item, "schedule_usage", text="", emboss=False)
            if context.active_object and not props.active_resource_id:
                row = layout.row(align=True)
                if item.ifc_definition_id in ResourceData.data["active_resource_ids"]:
                    op = row.operator("bim.unassign_resource", text="", icon="KEYFRAME_HLT", emboss=False)
                    op.resource = item.ifc_definition_id
                else:
                    op = row.operator("bim.assign_resource", text="", icon="KEYFRAME", emboss=False)
                    op.resource = item.ifc_definition_id

            if props.active_resource_id == item.ifc_definition_id:
                if props.editing_resource_type == "ATTRIBUTES":
                    row.operator("bim.edit_resource", text="", icon="CHECKMARK")
                elif props.editing_resource_type == "USAGE":
                    row.operator("bim.edit_resource_time", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_resource", text="", icon="CANCEL")
