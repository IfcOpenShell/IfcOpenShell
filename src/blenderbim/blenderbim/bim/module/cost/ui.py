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
import blenderbim.bim.module.cost.prop as CostProp
from bpy.types import Panel, UIList
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.cost.data import Data
from ifcopenshell.api.unit.data import Data as UnitData


class BIM_PT_cost_schedules(Panel):
    bl_label = "IFC Cost Schedules"
    bl_idname = "BIM_PT_cost_schedules"
    bl_options = {"DEFAULT_CLOSED"}
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"

    @classmethod
    def poll(cls, context):
        file = IfcStore.get_file()
        return file and hasattr(file, "schema") and file.schema != "IFC2X3"

    def draw(self, context):
        self.props = context.scene.BIMCostProperties

        if not Data.is_loaded:
            Data.load(IfcStore.get_file())

        if not UnitData.is_loaded:
            UnitData.load(IfcStore.get_file())

        row = self.layout.row()
        row.operator("bim.add_cost_schedule", icon="ADD")

        if self.props.active_cost_schedule_id:
            self.draw_cost_schedule_ui(
                self.props.active_cost_schedule_id, Data.cost_schedules[self.props.active_cost_schedule_id]
            )
        else:
            for cost_schedule_id, cost_schedule in Data.cost_schedules.items():
                self.draw_cost_schedule_ui(cost_schedule_id, cost_schedule)

    def draw_cost_schedule_ui(self, cost_schedule_id, cost_schedule):
        row = self.layout.row(align=True)
        row.label(text=cost_schedule["Name"] or "Unnamed", icon="LINENUMBERS_ON")

        if self.props.active_cost_schedule_id and self.props.active_cost_schedule_id == cost_schedule_id:
            op = row.operator("bim.select_cost_schedule_products", icon="RESTRICT_SELECT_OFF", text="")
            op.cost_schedule = cost_schedule_id
            row.prop(self.props, "should_show_column_ui", text="", icon="SHORTDISPLAY")
            if self.props.is_editing == "COST_SCHEDULE":
                row.operator("bim.edit_cost_schedule", text="", icon="CHECKMARK")
            elif self.props.is_editing == "COST_ITEMS":
                row.operator("bim.add_summary_cost_item", text="", icon="ADD").cost_schedule = cost_schedule_id
            row.operator("bim.disable_editing_cost_schedule", text="", icon="CANCEL")
        elif self.props.active_cost_schedule_id:
            row.operator("bim.remove_cost_schedule", text="", icon="X").cost_schedule = cost_schedule_id
        else:
            row.operator("bim.enable_editing_cost_items", text="", icon="OUTLINER").cost_schedule = cost_schedule_id
            row.operator(
                "bim.enable_editing_cost_schedule", text="", icon="GREASEPENCIL"
            ).cost_schedule = cost_schedule_id
            row.operator("bim.remove_cost_schedule", text="", icon="X").cost_schedule = cost_schedule_id

        if self.props.active_cost_schedule_id == cost_schedule_id:
            if self.props.is_editing == "COST_SCHEDULE":
                self.draw_editable_cost_schedule_ui()
            elif self.props.is_editing == "COST_ITEMS":
                if self.props.should_show_column_ui:
                    self.draw_column_ui()
                self.draw_editable_cost_item_ui(cost_schedule_id)

    def draw_column_ui(self):
        row = self.layout.row(align=True)
        row.prop(self.props, "cost_column", text="")
        row.operator("bim.add_cost_column", text="", icon="ADD").name = self.props.cost_column
        self.layout.template_list("BIM_UL_cost_columns", "", self.props, "columns", self.props, "active_column_index")

    def draw_editable_cost_schedule_ui(self):
        blenderbim.bim.helper.draw_attributes(self.props.cost_schedule_attributes, self.layout)

    def draw_editable_cost_item_ui(self, cost_schedule_id):
        row = self.layout.row(align=True)
        row.alignment = "RIGHT"
        ifc_definition_id = None
        if self.props.cost_items and self.props.active_cost_item_index < len(self.props.cost_items):
            ifc_definition_id = self.props.cost_items[self.props.active_cost_item_index].ifc_definition_id
        if ifc_definition_id:

            if Data.cost_schedules[self.props.active_cost_schedule_id]["PredefinedType"] != "SCHEDULEOFRATES":
                op = row.operator("bim.enable_editing_cost_item_quantities", text="", icon="PROPERTIES")
                op.cost_item = ifc_definition_id

            op = row.operator("bim.enable_editing_cost_item_values", text="", icon="DISC")
            op.cost_item = ifc_definition_id

            row.operator("bim.add_cost_item", text="", icon="ADD").cost_item = ifc_definition_id

            if self.props.active_cost_item_id == ifc_definition_id:
                if self.props.cost_item_editing_type == "ATTRIBUTES":
                    row.operator("bim.edit_cost_item", text="", icon="CHECKMARK")
                row.operator("bim.disable_editing_cost_item", text="", icon="CANCEL")
            else:
                op = row.operator("bim.enable_editing_cost_item", text="", icon="GREASEPENCIL")
                op.cost_item = ifc_definition_id

            row.operator("bim.remove_cost_item", text="", icon="X").cost_item = ifc_definition_id

        self.layout.template_list(
            "BIM_UL_cost_items",
            "",
            self.props,
            "cost_items",
            self.props,
            "active_cost_item_index",
        )
        if self.props.active_cost_item_id:
            if self.props.cost_item_editing_type == "ATTRIBUTES":
                self.draw_editable_cost_item_attributes_ui()
            elif self.props.cost_item_editing_type == "QUANTITIES":
                self.draw_editable_cost_item_quantities_ui()
            elif self.props.cost_item_editing_type == "VALUES":
                self.draw_editable_cost_item_values_ui()

    def draw_editable_cost_item_attributes_ui(self):
        blenderbim.bim.helper.draw_attributes(self.props.cost_item_attributes, self.layout)

    def draw_editable_cost_item_quantities_ui(self):
        row = self.layout.row(align=True)
        row.prop(self.props, "quantity_types", text="")
        op = row.operator("bim.add_cost_item_quantity", text="", icon="ADD")
        op.cost_item = self.props.active_cost_item_id
        op.ifc_class = self.props.quantity_types

        for quantity_id in Data.cost_items[self.props.active_cost_item_id]["CostQuantities"]:
            quantity = Data.physical_quantities[quantity_id]
            value = quantity[[k for k in quantity.keys() if "Value" in k][0]]
            row = self.layout.row(align=True)
            row.label(text=quantity["Name"])
            row.label(text="{0:.2f}".format(value))
            if self.props.active_cost_item_quantity_id and self.props.active_cost_item_quantity_id == quantity_id:
                op = row.operator("bim.edit_cost_item_quantity", text="", icon="CHECKMARK")
                op.physical_quantity = quantity_id
                row.operator("bim.disable_editing_cost_item_quantity", text="", icon="CANCEL")
            elif self.props.active_cost_item_quantity_id:
                op = row.operator("bim.remove_cost_item_quantity", text="", icon="X")
                op.cost_item = self.props.active_cost_item_id
                op.physical_quantity = quantity_id
            else:
                op = row.operator("bim.enable_editing_cost_item_quantity", text="", icon="GREASEPENCIL")
                op.physical_quantity = quantity_id
                op = row.operator("bim.remove_cost_item_quantity", text="", icon="X")
                op.cost_item = self.props.active_cost_item_id
                op.physical_quantity = quantity_id

            if self.props.active_cost_item_quantity_id and self.props.active_cost_item_quantity_id == quantity_id:
                box = self.layout.box()
                self.draw_editable_cost_item_quantity_ui(box)

    def draw_editable_cost_item_quantity_ui(self, layout):
        blenderbim.bim.helper.draw_attributes(self.props.quantity_attributes, self.layout)

    def draw_editable_cost_item_values_ui(self):
        row = self.layout.row(align=True)
        row.prop(self.props, "cost_types", text="")
        if self.props.cost_types == "CATEGORY":
            row.prop(self.props, "cost_category", text="")
        op = row.operator("bim.add_cost_value", text="", icon="ADD")
        op.parent = self.props.active_cost_item_id
        op.cost_type = self.props.cost_types
        if self.props.cost_types == "CATEGORY":
            op.cost_category = self.props.cost_category

        for cost_value_id in Data.cost_items[self.props.active_cost_item_id]["CostValues"]:
            row = self.layout.row(align=True)
            self.draw_readonly_cost_value_ui(row, cost_value_id)

        if self.props.cost_value_editing_type == "ATTRIBUTES":
            box = self.layout.box()
            self.draw_editable_cost_value_ui(box, Data.cost_values[self.props.active_cost_value_id])

    def draw_readonly_cost_value_ui(self, layout, cost_value_id):
        cost_value = Data.cost_values[cost_value_id]

        if self.props.active_cost_value_id == cost_value_id and self.props.cost_value_editing_type == "FORMULA":
            layout.prop(self.props, "cost_value_formula", text="")
        else:
            cost_value_label = "{0:.2f}".format(cost_value["AppliedValue"])
            cost_value_label += " = " + cost_value["Formula"]
            layout.label(text=cost_value_label, icon="DISC")

        self.draw_cost_value_operator_ui(layout, cost_value_id, self.props.active_cost_item_id)

    def draw_cost_value_operator_ui(self, layout, cost_value_id, parent_id):
        if self.props.active_cost_value_id and self.props.active_cost_value_id == cost_value_id:
            if self.props.cost_value_editing_type == "ATTRIBUTES":
                op = layout.operator("bim.edit_cost_item_value", text="", icon="CHECKMARK")
                op.cost_value = cost_value_id
            elif self.props.cost_value_editing_type == "FORMULA":
                op = layout.operator("bim.edit_cost_item_value_formula", text="", icon="CHECKMARK")
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

    def draw_editable_cost_value_ui(self, layout, cost_value):
        blenderbim.bim.helper.draw_attributes(self.props.cost_value_attributes, layout)


class BIM_PT_cost_item_types(Panel):
    bl_label = "IFC Cost Item Types"
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
        if Data.cost_schedules[props.active_cost_schedule_id]["PredefinedType"] != "SCHEDULEOFRATES":
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
    bl_label = "IFC Cost Item Quantities"
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
        if Data.cost_schedules[props.active_cost_schedule_id]["PredefinedType"] == "SCHEDULEOFRATES":
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
        row2.label(text="Elements")
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
        row2.template_list(
            "BIM_UL_cost_item_quantities",
            "",
            self.props,
            "cost_item_products",
            self.props,
            "active_cost_item_product_index",
        )

        if has_quantity_names:
            row2 = col.row()
            row2.prop(self.props, "product_quantity_names", text="")

        # Column2
        col = grid.column()

        has_quantity_names = CostProp.get_process_quantity_names(self, context)

        row2 = col.row(align=True)
        row2.label(text="Tasks")

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
        row2.template_list(
            "BIM_UL_cost_item_quantities",
            "",
            self.props,
            "cost_item_processes",
            self.props,
            "active_cost_item_process_index",
        )

        if has_quantity_names:
            row2 = col.row()
            row2.prop(self.props, "process_quantity_names", text="")

        # Column3
        col = grid.column()

        has_quantity_names = CostProp.get_resource_quantity_names(self, context)

        row2 = col.row(align=True)
        row2.label(text="Resources")

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
        row2.template_list(
            "BIM_UL_cost_item_quantities",
            "",
            self.props,
            "cost_item_resources",
            self.props,
            "active_cost_item_resource_index",
        )

        if has_quantity_names:
            row2 = col.row()
            row2.prop(self.props, "resource_quantity_names", text="")

class BIM_PT_cost_item_rates(Panel):
    bl_label = "IFC Cost Item Rates"
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
        if Data.cost_schedules[props.active_cost_schedule_id]["PredefinedType"] == "SCHEDULEOFRATES":
            return False
        if total_cost_items > 0 and props.active_cost_item_index < total_cost_items:
            return True
        return False

    def draw(self, context):
        self.props = context.scene.BIMCostProperties
        cost_item = self.props.cost_items[self.props.active_cost_item_index]
        row = self.layout.row(align=True)
        row.prop(self.props, "schedule_of_rates", text="")
        if self.props.active_cost_item_rate_index < len(self.props.cost_item_rates):
            op = row.operator("bim.assign_cost_value", text="", icon="COPYDOWN")
            op.cost_item = self.props.cost_items[self.props.active_cost_item_index].ifc_definition_id
            op.cost_rate = self.props.cost_item_rates[self.props.active_cost_item_rate_index].ifc_definition_id
        self.layout.template_list(
            "BIM_UL_cost_item_rates",
            "",
            self.props,
            "cost_item_rates",
            self.props,
            "active_cost_item_rate_index",
        )


class BIM_UL_cost_items_trait:
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if item:
            self.props = context.scene.BIMCostProperties
            cost_item = Data.cost_items[item.ifc_definition_id]
            row = layout.row(align=True)

            self.draw_hierarchy(row, item)

            split1 = row.split(factor=0.1)
            split1.prop(item, "identification", emboss=False, text="")
            split2 = split1.split(factor=0.5)
            split2.alignment = "RIGHT"
            split2.prop(item, "name", emboss=False, text="")

            self.draw_quantity_column(split2, cost_item)
            self.draw_value_column(split2, cost_item)

            for column in self.props.columns:
                split2.label(text=str(cost_item["CategoryValues"].get(column.name, "-")))

            self.draw_total_cost_column(split2, cost_item)
            # TODO: reimplement "bim.copy_cost_item_values" somewhere with better UX

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

    def draw_total_cost_column(self, layout, cost_item):
        layout.label(text="{0:.2f}".format(cost_item["TotalCost"]))

    def draw_quantity_column(self, layout, cost_item):
        if Data.cost_schedules[self.props.active_cost_schedule_id]["PredefinedType"] == "SCHEDULEOFRATES":
            self.draw_uom_column(layout, cost_item)
        else:
            self.draw_total_quantity_column(layout, cost_item)

    def draw_value_column(self, layout, cost_item):
        text = "{0:.2f}".format(cost_item["TotalAppliedValue"])
        if cost_item["UnitBasisValueComponent"] not in [None, 1]:
            text += " / {}".format(round(cost_item["UnitBasisValueComponent"], 2))
        layout.label(text=text)

    def draw_uom_column(self, layout, cost_item):
        layout.label(text=cost_item["UnitBasisUnitSymbol"] or "?" if cost_item["UnitBasisValueComponent"] else "-")

    def draw_total_quantity_column(self, layout, cost_item):
        layout.label(text="{0:.2f}".format(cost_item["TotalCostQuantity"]) + f" {cost_item['UnitSymbol'] or '?'}")


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
            row.split(factor=0.8)
            row.label(text=item.name)
            row.label(text="{0:.2f}".format(item.total_quantity))
            op = row.operator("bim.unassign_cost_item_quantity", text="", icon="X")
            op.cost_item = cost_item.ifc_definition_id
            op.related_object = item.ifc_definition_id
