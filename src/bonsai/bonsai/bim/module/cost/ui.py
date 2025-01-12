# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import bonsai.bim.helper
import bonsai.bim.module.cost.prop as CostProp
from bpy.types import Panel, UIList
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.cost.data import CostSchedulesData
from typing import Any


class BIM_PT_cost_schedules(Panel):
    bl_label = "Cost Schedules"
    bl_idname = "BIM_PT_cost_schedules"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_cost"
    bl_options = {"HIDE_HEADER"}

    @classmethod
    def poll(cls, context):
        file = IfcStore.get_file()
        return file and hasattr(file, "schema") and file.schema != "IFC2X3"

    def draw(self, context):
        if not CostSchedulesData.is_loaded:
            CostSchedulesData.load()

        self.props = context.scene.BIMCostProperties
        if not self.props.active_cost_schedule_id:
            row = self.layout.row(align=True)
            if CostSchedulesData.data["total_cost_schedules"]:
                row.alignment = "RIGHT"
                row.operator("bim.export_cost_schedules", icon="EXPORT", text="Export All Schedules")
                row = self.layout.row(align=True)
                row.label(text=f"{CostSchedulesData.data['total_cost_schedules']} Cost Schedules Found", icon="TEXT")
            else:
                row.label(text="No Cost Schedules found.", icon="TEXT")

            row.operator("bim.add_cost_schedule", icon="ADD", text="")
            row.operator("bim.import_cost_schedule_csv", icon="IMPORT", text="")

        for schedule in CostSchedulesData.data["schedules"]:
            self.draw_cost_schedule_ui(schedule)

    def draw_cost_schedule_ui(self, cost_schedule):
        row = self.layout.row(align=True)
        if self.props.active_cost_schedule_id and self.props.active_cost_schedule_id == cost_schedule["id"]:
            row.label(
                text="Currently editing: {}[{}]".format(cost_schedule["name"], cost_schedule["predefined_type"]),
                icon="LINENUMBERS_ON",
            )
            grid = self.layout.grid_flow(columns=2, even_columns=True)
            col = grid.column()
            row1 = col.row(align=True)
            row1.alignment = "LEFT"
            row1.label(text="Schedule tools")
            row1 = col.row(align=True)
            row1.alignment = "RIGHT"
            row1.operator("bim.export_cost_schedules", text="Export spreadsheet", icon="EXPORT").cost_schedule = (
                cost_schedule["id"]
            )
            row1.operator(
                "bim.generate_cost_schedule_browser", text="Generate spreadsheet browser", icon="URL"
            ).cost_schedule = cost_schedule["id"]
            row2 = col.row(align=True)
            row2.alignment = "RIGHT"
            op = row2.operator("bim.select_cost_schedule_products", icon="RESTRICT_SELECT_OFF", text="Assigned")
            op.cost_schedule = cost_schedule["id"]
            row2.operator("bim.select_unassigned_products", icon="RESTRICT_SELECT_OFF", text="Unassigned")

            col = grid.column()
            row1 = col.row(align=True)
            row1.alignment = "LEFT"
            row1.label(text="Settings")
            row1 = col.row(align=True)
            row1.alignment = "RIGHT"
            row1.prop(self.props, "should_show_currency_ui", text="Project Currency", icon="COPY_ID")
            row1.prop(self.props, "should_show_column_ui", text="Schedule Columns", icon="SHORTDISPLAY")
            if self.props.is_editing == "COST_SCHEDULE_ATTRIBUTES":
                row.operator("bim.edit_cost_schedule", text="", icon="CHECKMARK")
            row.operator("bim.disable_editing_cost_schedule", text="", icon="CANCEL")
        else:
            row.label(
                text="{}[{}]".format(cost_schedule["name"], cost_schedule["predefined_type"]), icon="LINENUMBERS_ON"
            )
            row.operator("bim.enable_editing_cost_items", text="", icon="OUTLINER").cost_schedule = cost_schedule["id"]
            row.operator("bim.enable_editing_cost_schedule_attributes", text="", icon="GREASEPENCIL").cost_schedule = (
                cost_schedule["id"]
            )
            row.operator("bim.remove_cost_schedule", text="", icon="X").cost_schedule = cost_schedule["id"]
        if self.props.active_cost_schedule_id == cost_schedule["id"]:
            if self.props.is_editing == "COST_SCHEDULE_ATTRIBUTES":
                self.draw_editable_cost_schedule_ui()
            elif self.props.is_editing == "COST_ITEMS":
                if self.props.should_show_column_ui:
                    self.draw_column_ui()
                if self.props.should_show_currency_ui:
                    self.draw_currency_ui()
                self.draw_editable_cost_item_ui()

    def draw_column_ui(self):
        row = self.layout.row(align=True)
        row.prop(self.props, "cost_column", text="")
        row.operator("bim.add_cost_column", text="", icon="ADD").name = self.props.cost_column
        self.layout.template_list("BIM_UL_cost_columns", "", self.props, "columns", self.props, "active_column_index")

    def draw_currency_ui(self):
        row = self.layout.row(align=True)
        if CostSchedulesData.data["currency"]:
            text = "Currency used: {}".format(CostSchedulesData.data["currency"]["name"])
            row.label(text=text)
            row.operator("bim.remove_unit", text="", icon="X").unit = CostSchedulesData.data["currency"]["id"]
        else:
            row.label(text="No currency set")
            row.prop(self.props, "currency", text="")
            if self.props.currency == "CUSTOM":
                row.alignment = "RIGHT"
                row.prop(self.props, "custom_currency", text="")
            row.operator("bim.add_currency", text="", icon="ADD")

    def draw_editable_cost_schedule_ui(self):
        bonsai.bim.helper.draw_attributes(self.props.cost_schedule_attributes, self.layout)

    def draw_editable_cost_item_ui(self):
        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        ifc_definition_id = None
        row = self.layout.row(align=True)
        row.label(text="Cost Item Tools")
        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        row.operator("bim.add_summary_cost_item", text="Add Summary Cost", icon="ADD")
        row.operator("bim.expand_cost_items", text="Expand All")
        row.operator("bim.contract_cost_items", text="Contract All")
        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        if self.props.cost_items and self.props.active_cost_item_index < len(self.props.cost_items):
            ifc_definition_id = self.props.cost_items[self.props.active_cost_item_index].ifc_definition_id
        if ifc_definition_id:
            row.prop(self.props, "show_cost_item_operators", text="Edit", icon="DOWNARROW_HLT")
            row.operator("bim.add_cost_item", text="Add", icon="ADD").cost_item = ifc_definition_id
            row.operator("bim.copy_cost_item", text="Copy", icon="ADD")
            row.operator("bim.remove_cost_item", text="Delete", icon="X").cost_item = ifc_definition_id
            if self.props.show_cost_item_operators:
                row = self.layout.row(align=True)
                row.alignment = "RIGHT"
                row.prop(self.props, "change_cost_item_parent", text="", icon="LINKED")
                row.prop(self.props, "enable_reorder", text="", icon="SORTALPHA")
                if not CostSchedulesData.data["is_editing_rates"]:
                    op = row.operator("bim.enable_editing_cost_item_quantities", text="", icon="PROPERTIES")
                    op.cost_item = ifc_definition_id
                op = row.operator("bim.enable_editing_cost_item_values", text="", icon="DISC")
                op.cost_item = ifc_definition_id
                if self.props.active_cost_item_id == ifc_definition_id:
                    if self.props.cost_item_editing_type == "ATTRIBUTES":
                        row.operator("bim.edit_cost_item", text="", icon="CHECKMARK")
                    row.operator("bim.disable_editing_cost_item", text="", icon="CANCEL")
                else:
                    op = row.operator("bim.enable_editing_cost_item_attributes", text="", icon="GREASEPENCIL")
                    op.cost_item = ifc_definition_id

        BIM_UL_cost_items_trait.draw_header(self.layout)
        self.layout.template_list(
            "BIM_UL_cost_items",
            "",
            self.props,
            "cost_items",
            self.props,
            "active_cost_item_index",
        )
        if self.props.active_cost_item_id:
            cost_item = CostSchedulesData.data["cost_items"][ifc_definition_id]
            if self.props.cost_item_editing_type == "ATTRIBUTES":
                self.draw_editable_cost_item_attributes_ui()
            elif self.props.cost_item_editing_type == "QUANTITIES":
                self.draw_editable_cost_item_quantities_ui(cost_item)
            elif self.props.cost_item_editing_type == "VALUES":
                self.draw_editable_cost_item_values_ui()

    def draw_editable_cost_item_attributes_ui(self):
        bonsai.bim.helper.draw_attributes(self.props.cost_item_attributes, self.layout)

    def draw_editable_cost_item_quantities_ui(self, cost_item: dict[str, Any]):
        quantities = CostSchedulesData.data["cost_quantities"]
        row = self.layout.row(align=True)
        # In IFC, all quantities of IfcCostTime should have 1 type.
        if quantities:
            quantity_class = cost_item["QuantityType"]
            row.label(text=quantity_class)
        else:
            row.prop(self.props, "quantity_types", text="")
            quantity_class = self.props.quantity_types

        op = row.operator("bim.add_cost_item_quantity", text="", icon="ADD")
        op.cost_item = self.props.active_cost_item_id
        op.ifc_class = quantity_class

        for quantity in quantities:
            row = self.layout.row(align=True)
            row.label(text=quantity["name"])
            row.label(text=quantity["value"])
            if self.props.active_cost_item_quantity_id and self.props.active_cost_item_quantity_id == quantity["id"]:
                op = row.operator("bim.edit_cost_item_quantity", text="", icon="CHECKMARK")
                op.physical_quantity = quantity["id"]
                row.operator("bim.disable_editing_cost_item_quantity", text="", icon="CANCEL")
            elif self.props.active_cost_item_quantity_id:
                op = row.operator("bim.remove_cost_item_quantity", text="", icon="X")
                op.cost_item = self.props.active_cost_item_id
                op.physical_quantity = quantity["id"]
            else:
                op = row.operator("bim.enable_editing_cost_item_quantity", text="", icon="GREASEPENCIL")
                op.physical_quantity = quantity["id"]
                op = row.operator("bim.remove_cost_item_quantity", text="", icon="X")
                op.cost_item = self.props.active_cost_item_id
                op.physical_quantity = quantity["id"]

            if self.props.active_cost_item_quantity_id and self.props.active_cost_item_quantity_id == quantity["id"]:
                bonsai.bim.helper.draw_attributes(self.props.quantity_attributes, self.layout.box())

    def draw_editable_cost_item_values_ui(self):
        row = self.layout.row(align=True)
        row.prop(self.props, "cost_types", text="")
        if self.props.cost_types == "FIXED":
            row.prop(self.props, "fixed_cost_value", text="")
        if self.props.cost_types == "CATEGORY":
            row.prop(self.props, "cost_category", text="")
        op = row.operator("bim.add_cost_value", text="Add Value", icon="ADD")
        op.parent = self.props.active_cost_item_id
        op.cost_type = self.props.cost_types
        if self.props.cost_types == "CATEGORY":
            op.cost_category = self.props.cost_category

        for cost_value in CostSchedulesData.data["cost_values"]:
            row = self.layout.row(align=True)
            self.draw_readonly_cost_value_ui(row, cost_value)

        if self.props.cost_value_editing_type == "ATTRIBUTES":
            bonsai.bim.helper.draw_attributes(self.props.cost_value_attributes, self.layout.box())

    def draw_readonly_cost_value_ui(self, layout, cost_value):
        if cost_value["name"]:
            layout.label(text=f"{cost_value['name']}: ")
        if self.props.active_cost_value_id == cost_value["id"] and self.props.cost_value_editing_type == "FORMULA":
            layout.prop(self.props, "cost_value_formula", text="")
        else:
            layout.label(text=cost_value["label"], icon="DISC")

        self.draw_cost_value_operator_ui(layout, cost_value["id"], self.props.active_cost_item_id)

    def draw_cost_value_operator_ui(self, layout, cost_value_id, parent_id):
        if self.props.active_cost_value_id and self.props.active_cost_value_id == cost_value_id:
            if self.props.cost_value_editing_type == "ATTRIBUTES":
                op = layout.operator("bim.edit_cost_value", text="", icon="CHECKMARK")
                op.cost_value = cost_value_id
            elif self.props.cost_value_editing_type == "FORMULA":
                op = layout.operator("bim.edit_cost_value_formula", text="", icon="CHECKMARK")
                op.cost_value = cost_value_id
            layout.operator("bim.disable_editing_cost_item_value", text="", icon="CANCEL")
        elif self.props.active_cost_value_id:
            op = layout.operator("bim.remove_cost_value", text="", icon="X")
            op.parent = parent_id
            op.cost_value = cost_value_id
        else:
            op = layout.operator("bim.enable_editing_cost_item_value_formula", text="", icon="CON_TRANSLIKE")
            op.cost_value = cost_value_id
            op = layout.operator("bim.enable_editing_cost_item_value", text="", icon="GREASEPENCIL")
            op.cost_value = cost_value_id
            op = layout.operator("bim.remove_cost_value", text="", icon="X")
            op.parent = parent_id
            op.cost_value = cost_value_id


class BIM_PT_cost_item_types(Panel):
    bl_label = "Cost Item Types"
    bl_idname = "BIM_PT_cost_item_types"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_cost_schedules"

    @classmethod
    def poll(cls, context):
        props = context.scene.BIMCostProperties
        total_cost_items = len(props.cost_items)
        if not props.active_cost_schedule_id:
            return False
        if not CostSchedulesData.is_loaded:
            return False
        if not CostSchedulesData.data["is_editing_rates"]:
            return False
        if total_cost_items > 0 and props.active_cost_item_index < total_cost_items:
            return True
        return False

    def draw(self, context):
        self.props = context.scene.BIMCostProperties
        cost_item = self.props.cost_items[self.props.active_cost_item_index]
        grid = self.layout.grid_flow(columns=3, even_columns=True)

        # Column1
        col = grid.column()

        row2 = col.row(align=True)
        row2.label(text="Elements")
        op = row2.operator("bim.assign_cost_item_type", text="", icon="ADD")
        op.cost_item = cost_item.ifc_definition_id
        op = row2.operator("bim.unassign_cost_item_type", text="", icon="REMOVE")
        op.cost_item = cost_item.ifc_definition_id
        op.related_object = 0
        op = row2.operator("bim.select_cost_item_products", icon="RESTRICT_SELECT_OFF", text="")
        op.cost_item = cost_item.ifc_definition_id

        row2 = col.row()
        row2.template_list(
            "BIM_UL_cost_item_types",
            "",
            self.props,
            "cost_item_type_products",
            self.props,
            "active_cost_item_type_product_index",
        )

        # Column2
        # TODO
        col = grid.column()

        row2 = col.row(align=True)
        row2.label(text="Tasks")

        row2 = col.row()
        row2.template_list(
            "BIM_UL_cost_item_quantities",
            "",
            self.props,
            "cost_item_processes",
            self.props,
            "active_cost_item_process_index",
        )

        # Column3
        # TODO
        col = grid.column()

        row2 = col.row(align=True)
        row2.label(text="Resources")

        row2 = col.row()
        row2.template_list(
            "BIM_UL_cost_item_quantities",
            "",
            self.props,
            "cost_item_resources",
            self.props,
            "active_cost_item_resource_index",
        )


class BIM_PT_cost_item_quantities(Panel):
    bl_label = "Cost Item Quantities"
    bl_idname = "BIM_PT_cost_item_quantities"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_cost_schedules"

    @classmethod
    def poll(cls, context):
        props = context.scene.BIMCostProperties
        total_cost_items = len(props.cost_items)
        if not props.active_cost_schedule_id:
            return False
        if not CostSchedulesData.is_loaded:
            return False
        if CostSchedulesData.data["is_editing_rates"]:
            return False
        if total_cost_items > 0 and props.active_cost_item_index < total_cost_items:
            return True
        return False

    def draw(self, context):
        self.props = context.scene.BIMCostProperties

        cost_item = self.props.cost_items[self.props.active_cost_item_index]

        grid = self.layout.grid_flow(columns=3, even_columns=True)

        # Column1
        col = grid.column()

        has_quantity_names = CostProp.get_product_quantity_names(self, context)

        row2 = col.row(align=True)
        total_cost_item_products = len(self.props.cost_item_products)
        row2.label(text="Elements ({})".format(total_cost_item_products))
        op = row2.operator("bim.select_cost_item_products", icon="RESTRICT_SELECT_OFF", text="")
        op.cost_item = cost_item.ifc_definition_id

        if context.selected_objects:
            if has_quantity_names:
                op = row2.operator("bim.assign_cost_item_quantity", text="", icon="PROPERTIES")
                op.related_object_type = "PRODUCT"
                op.cost_item = cost_item.ifc_definition_id
                op.prop_name = self.props.product_quantity_names

            op = row2.operator("bim.assign_cost_item_quantity", text="", icon="ADD")
            op.related_object_type = "PRODUCT"
            op.cost_item = cost_item.ifc_definition_id
            op.prop_name = ""

            op = row2.operator("bim.unassign_cost_item_quantity", text="", icon="REMOVE")
            op.cost_item = cost_item.ifc_definition_id
            op.related_object = 0

        row2 = col.row()
        row2.prop(self.props, "show_nested_elements", text="Show nested")
        row2 = col.row()
        row2.template_list(
            "BIM_UL_cost_item_quantities",
            "",
            self.props,
            "cost_item_products",
            self.props,
            "active_cost_item_product_index",
        )

        row2 = col.row()
        op = row2.operator("bim.clear_cost_item_assignments", text="Clear assignments", icon="X")
        op.cost_item = cost_item.ifc_definition_id
        op.related_object_type = "PRODUCT"

        if has_quantity_names:
            row2 = col.row()
            row2.prop(self.props, "product_quantity_names", text="")

        # Column2
        col = grid.column()

        has_quantity_names = CostProp.get_process_quantity_names(self, context)

        row2 = col.row(align=True)
        total_cost_item_processes = len(self.props.cost_item_processes)
        row2.label(text="Tasks ({})".format(total_cost_item_processes))

        tprops = context.scene.BIMTaskTreeProperties
        wprops = context.scene.BIMWorkScheduleProperties
        if tprops.tasks and wprops.active_task_index < len(tprops.tasks):
            if has_quantity_names:
                op = row2.operator("bim.assign_cost_item_quantity", text="", icon="PROPERTIES")
                op.related_object_type = "PROCESS"
                op.cost_item = cost_item.ifc_definition_id
                op.prop_name = self.props.process_quantity_names

            op = row2.operator("bim.assign_cost_item_quantity", text="", icon="ADD")
            op.related_object_type = "PROCESS"
            op.cost_item = cost_item.ifc_definition_id
            op.prop_name = ""

        row2 = col.row()
        row2.prop(self.props, "show_nested_tasks", text="Show nested")

        row2 = col.row()
        row2.template_list(
            "BIM_UL_cost_item_quantities",
            "",
            self.props,
            "cost_item_processes",
            self.props,
            "active_cost_item_process_index",
        )

        row2 = col.row()
        op = row2.operator("bim.clear_cost_item_assignments", text="Clear assignments", icon="X")
        op.cost_item = cost_item.ifc_definition_id
        op.related_object_type = "PROCESS"

        if has_quantity_names:
            row2 = col.row()
            row2.prop(self.props, "process_quantity_names", text="")

        # Column3
        col = grid.column()

        has_quantity_names = CostProp.get_resource_quantity_names(self, context)

        row2 = col.row(align=True)
        total_cost_item_resources = len(self.props.cost_item_resources)
        row2.label(text="Resources ({})".format(total_cost_item_resources))

        op = row2.operator("bim.calculate_cost_item_resource_value", text="", icon="DISC")
        op.cost_item = cost_item.ifc_definition_id

        rtprops = context.scene.BIMResourceTreeProperties
        rprops = context.scene.BIMResourceProperties
        if rtprops.resources and rprops.active_resource_index < len(rtprops.resources):
            if has_quantity_names:
                op = row2.operator("bim.assign_cost_item_quantity", text="", icon="PROPERTIES")
                op.related_object_type = "RESOURCE"
                op.cost_item = cost_item.ifc_definition_id
                op.prop_name = self.props.resource_quantity_names

            op = row2.operator("bim.assign_cost_item_quantity", text="", icon="ADD")
            op.related_object_type = "RESOURCE"
            op.cost_item = cost_item.ifc_definition_id
            op.prop_name = ""

        row2 = col.row()
        row2.prop(self.props, "show_nested_resources", text="Show nested")

        row2 = col.row()
        row2.template_list(
            "BIM_UL_cost_item_quantities",
            "",
            self.props,
            "cost_item_resources",
            self.props,
            "active_cost_item_resource_index",
        )

        row2 = col.row()
        op = row2.operator("bim.clear_cost_item_assignments", text="Clear assignments", icon="X")
        op.cost_item = cost_item.ifc_definition_id
        op.related_object_type = "RESOURCE"

        if has_quantity_names:
            row2 = col.row()
            row2.prop(self.props, "resource_quantity_names", text="")


class BIM_PT_cost_item_rates(Panel):
    bl_label = "Cost Item Rates"
    bl_idname = "BIM_PT_cost_item_rates"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_cost_schedules"

    @classmethod
    def poll(cls, context):
        props = context.scene.BIMCostProperties
        total_cost_items = len(props.cost_items)
        if not props.active_cost_schedule_id:
            return False
        if not CostSchedulesData.is_loaded:
            return False
        if CostSchedulesData.data["is_editing_rates"]:
            return False
        if total_cost_items > 0 and props.active_cost_item_index < total_cost_items:
            return True
        return False

    def draw(self, context):
        self.props = context.scene.BIMCostProperties
        row = self.layout.row(align=True)
        row.prop(self.props, "schedule_of_rates", text="")
        if self.props.active_cost_item_rate_index < len(self.props.cost_item_rates):
            cost_item = self.props.cost_items[self.props.active_cost_item_index]
            cost_item_rate = self.props.cost_item_rates[self.props.active_cost_item_rate_index]
            op = row.operator("bim.assign_cost_value", text="", icon="COPYDOWN")
            op.cost_item = cost_item.ifc_definition_id
            op.cost_rate = cost_item_rate.ifc_definition_id
        self.layout.template_list(
            "BIM_UL_cost_item_rates",
            "",
            self.props,
            "cost_item_rates",
            self.props,
            "active_cost_item_rate_index",
        )


class BIM_UL_cost_items_trait:
    @classmethod
    def draw_header(cls, layout: bpy.types.UILayout):
        row = layout.row(align=True)

        split1 = row.split(factor=0.1)
        split1.label(text="ID")

        split2 = split1.split(factor=0.5)
        split2.alignment = "RIGHT"
        split2.label(text="Name")
        if CostSchedulesData.data["is_editing_rates"]:
            split2.label(text="Unit")
        else:
            split2.label(text="Quantity")
        split2.label(text="Value")

        for column in bpy.context.scene.BIMCostProperties.columns:
            split2.label(text=column.name)
        split2.label(text="Total Cost")

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            self.props = context.scene.BIMCostProperties
            cost_item = CostSchedulesData.data["cost_items"][item.ifc_definition_id]
            row = layout.row(align=True)

            self.draw_hierarchy(row, item)

            split1 = row.split(factor=0.1)
            split1.prop(item, "identification", emboss=False, text="")
            split2 = split1.split(factor=0.5)
            split2.alignment = "RIGHT"
            split2.prop(item, "name", emboss=False, text="")

            self.draw_quantity_column(split2, cost_item)
            self.draw_value_column(split2, cost_item)
            if self.props.active_cost_item_id == item.ifc_definition_id:
                row.operator("bim.disable_editing_cost_item", text="", icon="CANCEL")

            for column in self.props.columns:
                split2.label(text=str(cost_item["CategoryValues"].get(column.name, "-")))

            self.draw_total_cost_column(split2, cost_item)
            if self.props.enable_reorder:
                self.draw_order_operator(row, item.ifc_definition_id, cost_item)

            if self.props.change_cost_item_parent:
                self.draw_parent_operator(row, item.ifc_definition_id)

            # TODO: reimplement "bim.copy_cost_item_values" somewhere with better UX

    def draw_parent_operator(self, row, cost_item_id):
        if self.props.active_cost_item_id:
            if self.props.active_cost_item_id != cost_item_id:
                op = row.operator("bim.change_parent_cost_item", text="", icon="LINKED", emboss=False).new_parent = (
                    cost_item_id
                )
            else:
                row.label(text="", icon="BLANK1")

    def draw_hierarchy(self, row, item):
        for i in range(0, item.level_index):
            row.label(text="", icon="BLANK1")
        if item.has_children:
            if item.is_expanded:
                op = row.operator(self.contract_operator, text="", emboss=False, icon="DISCLOSURE_TRI_DOWN")
            else:
                op = row.operator(self.expand_operator, text="", emboss=False, icon="DISCLOSURE_TRI_RIGHT")
            op.cost_item = item.ifc_definition_id
        else:
            row.label(text="", icon="DOT")

    def draw_quantity_column(self, layout, cost_item):
        if CostSchedulesData.data["is_editing_rates"]:
            self.draw_uom_column(layout, cost_item)
        else:
            self.draw_total_quantity_column(layout, cost_item)

    def draw_uom_column(self, layout, cost_item):
        layout.label(text=cost_item["UnitBasisUnitSymbol"])

    def draw_total_quantity_column(self, layout, cost_item):
        if cost_item["TotalCostQuantity"] is not None:
            label = "{0:.2f}".format(cost_item["TotalCostQuantity"]) + f" {cost_item['UnitSymbol'] or '-'}"
            layout.label(text=label)
        else:
            layout.label(text="-")

    def draw_value_column(self, layout, cost_item):
        if cost_item["TotalAppliedValue"]:
            text = "{0:,.2f}".format(cost_item["TotalAppliedValue"]).replace(",", " ")
            if cost_item["UnitBasisValueComponent"] not in [None, 1]:
                text = "{} / {}".format(text, round(cost_item["UnitBasisValueComponent"], 2))
            currency = CostSchedulesData.data["currency"]
            text = "{} {}".format(text, currency["name"]) if currency else text
            layout.label(text=text)
        else:
            layout.label(text="-")

    def draw_total_cost_column(self, layout, cost_item):
        format_numbers = "{0:,.2f}".format(cost_item["TotalCost"]).replace(",", " ")
        currency = CostSchedulesData.data["currency"]
        text = "{} {}".format(format_numbers, currency["name"]) if currency else format_numbers
        layout.label(text=text)

    def draw_order_operator(self, row, ifc_definition_id, cost_item):
        if cost_item["NestingIndex"] is not None:
            if cost_item["NestingIndex"] == 0:
                op = row.operator("bim.reorder_cost_item_nesting", icon="TRIA_DOWN", text="")
                op.cost_item = ifc_definition_id
                op.new_index = cost_item["NestingIndex"] + 1
            elif cost_item["NestingIndex"] > 0:
                op = row.operator("bim.reorder_cost_item_nesting", icon="TRIA_UP", text="")
                op.cost_item = ifc_definition_id
                op.new_index = cost_item["NestingIndex"] - 1


class BIM_UL_cost_items(BIM_UL_cost_items_trait, UIList):
    def __init__(self):
        self.contract_operator = "bim.contract_cost_item"
        self.expand_operator = "bim.expand_cost_item"


class BIM_UL_cost_item_rates(BIM_UL_cost_items_trait, UIList):
    # A schedule of rates UIList is identical to a regular cost items UIList but
    # we want a separate UIList instance so that you can browse both lists
    # independently in Blender. So we use a trait.
    def __init__(self):
        self.contract_operator = "bim.contract_cost_item_rate"
        self.expand_operator = "bim.expand_cost_item_rate"

    def draw_quantity_column(self, layout, cost_item):
        self.draw_uom_column(layout, cost_item)

    def draw_total_cost_column(self, layout, cost_item):
        pass  # No such thing as a total cost in a schedule of rates


class BIM_UL_cost_columns(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        props = context.scene.BIMCostProperties
        if item:
            row = layout.row(align=True)
            row.prop(item, "name", emboss=False, text="")
            row.operator("bim.remove_cost_column", text="", icon="X").name = item.name


class BIM_UL_cost_item_types(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        props = context.scene.BIMCostProperties
        cost_item = props.cost_items[props.active_cost_item_index]

        if item:
            row = layout.row(align=True)
            row.label(text=item.name)
            op = row.operator("bim.unassign_cost_item_type", text="", icon="X")
            op.cost_item = cost_item.ifc_definition_id
            op.related_object = item.ifc_definition_id


class BIM_UL_cost_item_quantities(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        props = context.scene.BIMCostProperties
        cost_item = props.cost_items[props.active_cost_item_index]
        if item:
            row = layout.row(align=True)
            op = row.operator("bim.select_product", text="", icon="RESTRICT_SELECT_OFF")
            op.product = item.ifc_definition_id
            row.split(factor=0.8)
            row.label(text=item.name)
            formatted_quantity = "{0:.2f}".format(item.total_quantity)
            row.label(text="{}{}".format(formatted_quantity, item.unit_symbol))
            op = row.operator("bim.unassign_cost_item_quantity", text="", icon="X")
            op.cost_item = cost_item.ifc_definition_id
            op.related_object = item.ifc_definition_id


class BIM_UL_product_cost_items(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            row = layout.row(align=True)
            op = row.operator("bim.highlight_product_cost_item", text="", icon="STYLUS_PRESSURE")
            op.cost_item = item.ifc_definition_id
            row.split(factor=0.5)
            row.label(text=item.name)
            qty = "{0:.2f}".format(item.total_quantity)
            formatted_total_quantity = "{0:.2f}".format(item.total_cost_quantity)
            row.label(text="{}/{} {}".format(qty, formatted_total_quantity, item.unit_symbol))


class BIM_PT_Costing_Tools(Panel):
    bl_label = "5D Tools"
    bl_idname = "BIM_PT_Costing_Tools"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    bl_parent_id = "BIM_PT_tab_cost"

    def draw(self, context):
        self.props = context.scene.BIMCostProperties
        row = self.layout.row()
        row.operator("bim.load_product_cost_items", icon="FILE_REFRESH")
        row = self.layout.row()
        row.template_list(
            "BIM_UL_product_cost_items",
            "",
            self.props,
            "product_cost_items",
            self.props,
            "active_product_cost_item_index",
        )
