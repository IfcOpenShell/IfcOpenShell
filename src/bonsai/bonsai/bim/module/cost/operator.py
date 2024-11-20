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
import ifcopenshell.api
import bonsai.tool as tool
from bpy_extras.io_utils import ImportHelper
import bonsai.tool as tool
import bonsai.core.cost as core


class AddCostSchedule(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_cost_schedule"
    bl_label = "Add Cost Schedule"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add a new cost schedule"
    name: bpy.props.StringProperty()
    object_type: bpy.props.StringProperty()

    def _execute(self, context):
        predefined_type = context.scene.BIMCostProperties.cost_schedule_predefined_types
        if predefined_type == "USERDEFINED":
            predefined_type = self.object_type
        core.add_cost_schedule(tool.Ifc, name=self.name, predefined_type=predefined_type)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "name", text="Name")
        layout.prop(context.scene.BIMCostProperties, "cost_schedule_predefined_types", text="Type")
        if context.scene.BIMCostProperties.cost_schedule_predefined_types == "USERDEFINED":
            layout.prop(self, "object_type", text="Object type")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


class EditCostSchedule(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_cost_schedule"
    bl_label = "Edit Cost Schedule"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_cost_schedule(
            tool.Ifc,
            tool.Cost,
            cost_schedule=tool.Ifc.get().by_id(context.scene.BIMCostProperties.active_cost_schedule_id),
        )


class RemoveCostSchedule(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_cost_schedule"
    bl_label = "Remove Cost Schedule"
    bl_options = {"REGISTER", "UNDO"}
    cost_schedule: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_cost_schedule(tool.Ifc, tool.Cost, cost_schedule=tool.Ifc.get().by_id(self.cost_schedule))


class EnableEditingCostSchedule(bpy.types.Operator):
    bl_idname = "bim.enable_editing_cost_schedule_attributes"
    bl_label = "Enable Editing Cost Schedule"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Enable editing cost schedule"
    cost_schedule: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_cost_schedule_attributes(tool.Cost, cost_schedule=tool.Ifc.get().by_id(self.cost_schedule))
        return {"FINISHED"}


class EnableEditingCostItems(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_cost_items"
    bl_label = "Enable Editing Cost Items"
    bl_options = {"REGISTER", "UNDO"}
    cost_schedule: bpy.props.IntProperty()

    def _execute(self, context):
        core.enable_editing_cost_items(tool.Cost, cost_schedule=tool.Ifc.get().by_id(self.cost_schedule))


class DisableEditingCostSchedule(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_cost_schedule"
    bl_label = "Disable Editing Cost Schedule"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_cost_schedule(tool.Cost)


class AddSummaryCostItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_summary_cost_item"
    bl_label = "Add Cost Item"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add a summary cost item"

    def _execute(self, context):
        core.add_summary_cost_item(tool.Ifc, tool.Cost, cost_schedule=tool.Cost.get_active_cost_schedule())


class AddCostItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_cost_item"
    bl_label = "Add Cost Item"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add a new cost item"
    cost_item: bpy.props.IntProperty()

    def _execute(self, context):
        core.add_cost_item(tool.Ifc, tool.Cost, cost_item=tool.Ifc.get().by_id(self.cost_item))


class CopyCostItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.copy_cost_item"
    bl_label = "Copy Cost Item"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Copy a cost item"

    def _execute(self, context):
        core.copy_cost_item(tool.Ifc, tool.Cost)


class ExpandCostItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.expand_cost_item"
    bl_label = "Expand Cost Item"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Expand this cost item"
    cost_item: bpy.props.IntProperty()

    def _execute(self, context):
        core.expand_cost_item(tool.Cost, cost_item=tool.Ifc.get().by_id(self.cost_item))


class ExpandCostItems(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.expand_cost_items"
    bl_label = "Expand Cost Items"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Expand all cost items"
    cost_items: bpy.props.StringProperty()

    def _execute(self, context):
        core.expand_cost_items(tool.Cost)


class ContractCostItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.contract_cost_item"
    bl_label = "Contract Cost Item"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Contract a cost item"
    cost_item: bpy.props.IntProperty()

    def _execute(self, context):
        core.contract_cost_item(tool.Cost, cost_item=tool.Ifc.get().by_id(self.cost_item))


class ContractCostItems(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.contract_cost_items"
    bl_label = "Contract Cost Item"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Collapse cost item tree"
    cost_item: bpy.props.IntProperty()

    def _execute(self, context):
        core.contract_cost_items(tool.Cost)


class RemoveCostItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_cost_item"
    bl_label = "Remove Cost Item"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_cost_item(tool.Ifc, tool.Cost, cost_item_id=self.cost_item)


class EnableEditingCostItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_cost_item_attributes"
    bl_label = "Enable Editing Cost Item"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()

    def _execute(self, context):
        core.enable_editing_cost_item_attributes(tool.Cost, cost_item=tool.Ifc.get().by_id(self.cost_item))


class DisableEditingCostItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.disable_editing_cost_item"
    bl_label = "Disable Editing Cost Item"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.disable_editing_cost_item(tool.Cost)


class EditCostItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_cost_item"
    bl_label = "Edit Cost Item"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.edit_cost_item(tool.Ifc, tool.Cost)
        return {"FINISHED"}


class AssignCostItemType(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_cost_item_type"
    bl_label = "Assign Cost Item To Product Types"
    bl_description = "Assign cost item to currently selected or active product types"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()
    prop_name: bpy.props.StringProperty()

    def _execute(self, context):
        product_types = core.assign_cost_item_type(
            tool.Ifc,
            tool.Cost,
            tool.Spatial,
            cost_item=tool.Ifc.get().by_id(self.cost_item),
            prop_name=self.prop_name,  # TODO: REVIEW PROP_NAME USABILITY
        )
        self.report({"INFO"}, f"Cost item was assigned to {len(product_types)} product types.")


class UnassignCostItemType(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_cost_item_type"
    bl_label = "Unassign Cost Item Type"
    bl_description = "Unassign cost item from currently selected or active product types"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()
    related_object: bpy.props.IntProperty()

    def _execute(self, context):
        product_types = core.unassign_cost_item_type(
            tool.Ifc,
            tool.Cost,
            tool.Spatial,
            cost_item=tool.Ifc.get().by_id(self.cost_item),
            product_types=[tool.Ifc.get().by_id(self.related_object)] if self.related_object else None,
        )
        self.report({"INFO"}, f"Cost item was unassigned from {len(product_types)} product types.")
        return {"FINISHED"}


class AssignCostItemQuantity(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_cost_item_quantity"
    bl_label = "Assign Cost Item Quantity"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()
    related_object_type: bpy.props.StringProperty()
    prop_name: bpy.props.StringProperty()

    def _execute(self, context):
        result = core.assign_cost_item_quantity(
            tool.Ifc,
            tool.Cost,
            cost_item=tool.Ifc.get().by_id(self.cost_item),
            related_object_type=self.related_object_type,
            prop_name=self.prop_name,  # TODO: REVIEW PROP_NAME USABILITY
        )
        if not result:
            self.report(
                {"ERROR"},
                f"Cost item wasn't assigned - no objects of type '{self.related_object_type}' are selected.",
            )


class UnassignCostItemQuantity(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.unassign_cost_item_quantity"
    bl_label = "Unassign Cost Item Quantity"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Unassign cost item quantity"
    cost_item: bpy.props.IntProperty()
    related_object: bpy.props.IntProperty()

    def _execute(self, context):
        core.unassign_cost_item_quantity(
            tool.Ifc,
            tool.Cost,
            cost_item=tool.Ifc.get().by_id(self.cost_item),
            products=(
                [tool.Ifc.get().by_id(self.related_object)]
                if self.related_object
                else tool.Spatial.get_selected_products()
            ),
        )


class EnableEditingCostItemQuantities(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_cost_item_quantities"
    bl_label = "Enable Editing Cost Item Quantities"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Enable editing cost item quantities"
    cost_item: bpy.props.IntProperty()

    def _execute(self, context):
        core.enable_editing_cost_item_quantities(tool.Cost, cost_item=tool.Ifc.get().by_id(self.cost_item))


class EnableEditingCostItemValues(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_cost_item_values"
    bl_label = "Enable Editing Cost Item Values"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Enable editing cost item values"
    cost_item: bpy.props.IntProperty()

    def _execute(self, context):
        core.enable_editing_cost_item_values(tool.Cost, cost_item=tool.Ifc.get().by_id(self.cost_item))


class AddCostItemQuantity(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_cost_item_quantity"
    bl_label = "Add Cost Item Quantity"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Add cost item quantity"
    cost_item: bpy.props.IntProperty()
    ifc_class: bpy.props.StringProperty()

    def _execute(self, context):
        core.add_cost_item_quantity(tool.Ifc, cost_item=tool.Ifc.get().by_id(self.cost_item), ifc_class=self.ifc_class)


class RemoveCostItemQuantity(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_cost_item_quantity"
    bl_label = "Remove Cost Item Quantity"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Remove cost item quantity"
    cost_item: bpy.props.IntProperty()
    physical_quantity: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_cost_item_quantity(
            tool.Ifc,
            cost_item=tool.Ifc.get().by_id(self.cost_item),
            physical_quantity=tool.Ifc.get().by_id(self.physical_quantity),
        )


class EnableEditingCostItemQuantity(bpy.types.Operator):
    bl_idname = "bim.enable_editing_cost_item_quantity"
    bl_label = "Enable Editing Cost Item Quantity"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Enable editing cost item quantity"
    physical_quantity: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_cost_item_quantity(
            tool.Cost, physical_quantity=tool.Ifc.get().by_id(self.physical_quantity)
        )
        return {"FINISHED"}


class DisableEditingCostItemQuantity(bpy.types.Operator):
    bl_idname = "bim.disable_editing_cost_item_quantity"
    bl_label = "Disable Editing Cost Item Quantity"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Disable editing cost item quantity"

    def execute(self, context):
        core.disable_editing_cost_item_quantity(tool.Cost)
        return {"FINISHED"}


class EditCostItemQuantity(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_cost_item_quantity"
    bl_label = "Edit Cost Item Quantity"
    bl_options = {"REGISTER", "UNDO"}
    physical_quantity: bpy.props.IntProperty()

    def _execute(self, context):
        core.edit_cost_item_quantity(
            tool.Ifc, tool.Cost, physical_quantity=tool.Ifc.get().by_id(self.physical_quantity)
        )


class AddCostValue(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_cost_value"
    bl_label = "Add Cost Value"
    bl_options = {"REGISTER", "UNDO"}
    parent: bpy.props.IntProperty()
    cost_type: bpy.props.StringProperty()
    cost_category: bpy.props.StringProperty()

    def _execute(self, context):
        core.add_cost_value(
            tool.Ifc,
            tool.Cost,
            parent=tool.Ifc.get().by_id(self.parent),
            cost_type=self.cost_type,
            cost_category=self.cost_category,
        )
        return {"FINISHED"}


class RemoveCostItemValue(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_cost_value"
    bl_label = "Remove Cost Item Value"
    bl_options = {"REGISTER", "UNDO"}
    parent: bpy.props.IntProperty()
    cost_value: bpy.props.IntProperty()

    def _execute(self, context):
        core.remove_cost_value(
            tool.Ifc, parent=tool.Ifc.get().by_id(self.parent), cost_value=tool.Ifc.get().by_id(self.cost_value)
        )
        return {"FINISHED"}


class EnableEditingCostItemValue(bpy.types.Operator):
    bl_idname = "bim.enable_editing_cost_item_value"
    bl_label = "Enable Editing Cost Item Value"
    bl_options = {"REGISTER", "UNDO"}
    cost_value: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_cost_item_value(tool.Cost, cost_value=tool.Ifc.get().by_id(self.cost_value))
        return {"FINISHED"}


class DisableEditingCostItemValue(bpy.types.Operator):
    bl_idname = "bim.disable_editing_cost_item_value"
    bl_label = "Disable Editing Cost Item Value"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.disable_editing_cost_item_value(tool.Cost)
        return {"FINISHED"}


class EnableEditingCostItemValueFormula(bpy.types.Operator):
    bl_idname = "bim.enable_editing_cost_item_value_formula"
    bl_label = "Enable Editing Cost Item Value Formula"
    bl_options = {"REGISTER", "UNDO"}
    cost_value: bpy.props.IntProperty()

    def execute(self, context):
        core.enable_editing_cost_item_value_formula(tool.Cost, cost_value=tool.Ifc.get().by_id(self.cost_value))
        return {"FINISHED"}


class EditCostItemValueFormula(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_cost_value_formula"
    bl_label = "Edit Cost Value Formula"
    bl_options = {"REGISTER", "UNDO"}
    cost_value: bpy.props.IntProperty()

    def _execute(self, context):
        core.edit_cost_item_value_formula(tool.Ifc, tool.Cost, cost_value=tool.Ifc.get().by_id(self.cost_value))
        return {"FINISHED"}


class EditCostItemValue(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.edit_cost_value"
    bl_label = "Edit Cost Value"
    bl_options = {"REGISTER", "UNDO"}
    cost_value: bpy.props.IntProperty()

    def _execute(self, context):
        core.edit_cost_value(tool.Ifc, tool.Cost, cost_value=tool.Ifc.get().by_id(self.cost_value))
        return {"FINISHED"}


class CopyCostItemValues(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.copy_cost_item_values"
    bl_label = "Copy Cost Item Values"
    bl_options = {"REGISTER", "UNDO"}
    source: bpy.props.IntProperty()
    destination: bpy.props.IntProperty()

    def _execute(self, context):
        core.copy_cost_item_values(
            tool.Ifc,
            tool.Cost,
            source=tool.Ifc.get().by_id(self.source),
            destination=tool.Ifc.get().by_id(self.destination),
        )
        return {"FINISHED"}


class SelectCostItemProducts(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.select_cost_item_products"
    bl_label = "Select Cost Item Products"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()

    def _execute(self, context):
        core.select_cost_item_products(tool.Cost, tool.Spatial, cost_item=tool.Ifc.get().by_id(self.cost_item))
        return {"FINISHED"}


class SelectCostScheduleProducts(bpy.types.Operator):
    bl_idname = "bim.select_cost_schedule_products"
    bl_label = "Select Cost Schedule Products"
    bl_options = {"REGISTER", "UNDO"}
    cost_schedule: bpy.props.IntProperty()

    def execute(self, context):
        core.select_cost_schedule_products(
            tool.Cost, tool.Spatial, cost_schedule=tool.Ifc.get().by_id(self.cost_schedule)
        )
        return {"FINISHED"}


class ImportCostScheduleCsv(bpy.types.Operator, ImportHelper, tool.Ifc.Operator):
    bl_idname = "bim.import_cost_schedule_csv"
    bl_label = "Import Cost Schedule CSV"
    bl_options = {"REGISTER", "UNDO"}
    filename_ext = ".csv"
    filter_glob: bpy.props.StringProperty(default="*.csv", options={"HIDDEN"})
    is_schedule_of_rates: bpy.props.BoolProperty(name="Is Schedule Of Rates", default=False)

    @classmethod
    def poll(cls, context):
        ifc_file = tool.Ifc.get()
        if ifc_file is None:
            cls.poll_message_set("No IFC file is loaded.")
            return False
        return True

    def _execute(self, context):
        core.import_cost_schedule_csv(tool.Cost, self.filepath, self.is_schedule_of_rates)
        return {"FINISHED"}


class AddCostColumn(bpy.types.Operator):
    bl_idname = "bim.add_cost_column"
    bl_label = "Add Cost Column"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        if not context.scene.BIMCostProperties.cost_column:
            cls.poll_message_set("Cost column name is empty")
            return False
        return True

    def execute(self, context):
        core.add_cost_column(tool.Cost, self.name)
        return {"FINISHED"}


class RemoveCostColumn(bpy.types.Operator):
    bl_idname = "bim.remove_cost_column"
    bl_label = "Remove Cost Column"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty()

    def execute(self, context):
        core.remove_cost_column(tool.Cost, self.name)
        return {"FINISHED"}


class LoadCostItemQuantities(bpy.types.Operator):
    bl_idname = "bim.load_cost_item_quantities"
    bl_label = "Load Cost Item Quantities"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.load_cost_item_quantities(tool.Cost)
        return {"FINISHED"}


class LoadCostItemElementQuantities(bpy.types.Operator):
    bl_idname = "bim.load_cost_item_element_quantities"
    bl_label = "Load Cost Item Element Quantities"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.load_cost_item_element_quantities(tool.Cost)
        return {"FINISHED"}


class LoadCostItemTaskQuantities(bpy.types.Operator):
    bl_idname = "bim.load_cost_item_task_quantities"
    bl_label = "Load Cost Item Task Quantities"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.load_cost_item_task_quantities(tool.Cost)
        return {"FINISHED"}


class LoadCostItemResourceQuantities(bpy.types.Operator):
    bl_idname = "bim.load_cost_item_resource_quantities"
    bl_label = "Load Cost Item Resource Quantities"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.load_cost_item_resource_quantities(tool.Cost)
        return {"FINISHED"}


class LoadCostItemTypes(bpy.types.Operator):
    bl_idname = "bim.load_cost_item_types"
    bl_label = "Load Cost Item Types"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.load_cost_item_types(tool.Cost)
        return {"FINISHED"}


class AssignCostValue(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.assign_cost_value"
    bl_label = "Assign Cost Rate Value"
    bl_description = "Assign cost rate value to active cost item"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()
    cost_rate: bpy.props.IntProperty()

    def _execute(self, context):
        core.assign_cost_value(
            tool.Ifc, cost_item=tool.Ifc.get().by_id(self.cost_item), cost_rate=tool.Ifc.get().by_id(self.cost_rate)
        )


class LoadScheduleOfRates(bpy.types.Operator):
    bl_idname = "bim.load_schedule_of_rates_tree"
    bl_label = "Load Schedule of Rates"
    bl_options = {"REGISTER", "UNDO"}
    cost_schedule: bpy.props.IntProperty()

    def execute(self, context):
        core.load_schedule_of_rates_tree(tool.Cost, schedule_of_rates=tool.Ifc.get().by_id(self.cost_schedule))
        return {"FINISHED"}


class ExpandCostItemRate(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.expand_cost_item_rate"
    bl_label = "Expand Cost Item Rate"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()

    def _execute(self, context):
        core.expand_cost_item_rate(tool.Cost, self.cost_item)
        return {"FINISHED"}


class ContractCostItemRate(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.contract_cost_item_rate"
    bl_label = "Contract Cost Item Rate"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()

    def _execute(self, context):
        core.contract_cost_item_rate(tool.Cost, self.cost_item)
        return {"FINISHED"}


class CalculateCostItemResourceValue(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.calculate_cost_item_resource_value"
    bl_label = "Calculate Cost Item Resource Value"
    bl_description = "Calculate cost item value based on it's resources. Any previous cost values are removed"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()

    def _execute(self, context):
        core.calculate_cost_item_resource_value(tool.Ifc, cost_item=tool.Ifc.get().by_id(self.cost_item))
        return {"FINISHED"}


class ExportCostSchedules(bpy.types.Operator):
    bl_idname = "bim.export_cost_schedules"
    bl_label = "Export Cost Schedule"
    bl_options = {"REGISTER", "UNDO"}
    bl_description = "Export a cost schedule to a CSV, XSLX OR ODS file"
    cost_schedule: bpy.props.IntProperty()
    format: bpy.props.EnumProperty(name="Format", items=(("CSV", "CSV", ""), ("XLSX", "XLSX", ""), ("ODS", "ODS", "")))
    directory: bpy.props.StringProperty(subtype="FILE_PATH")
    filter_folder: bpy.props.BoolProperty(
        name="Filter Folders",
        default=True,
    )

    def execute(self, context):
        cost_schedule = tool.Ifc.get().by_id(self.cost_schedule) if self.cost_schedule else None
        r = core.export_cost_schedules(
            tool.Cost, filepath=self.directory, format=self.format, cost_schedule=cost_schedule
        )
        if isinstance(r, str):
            self.report({"ERROR"}, r)
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def draw(self, context):
        self.layout.label(text="Choose a format")
        self.layout.prop(self, "format")
        self.layout.label(text="Select a directory.")


class ClearCostItemAssignments(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.clear_cost_item_assignments"
    bl_label = "Clear Cost Item Product Assignments"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()
    related_object_type: bpy.props.StringProperty()

    def _execute(self, context):
        core.clear_cost_item_assignments(
            tool.Ifc,
            tool.Cost,
            cost_item=tool.Ifc.get().by_id(self.cost_item),
            related_object_type=self.related_object_type,
        )
        return {"FINISHED"}


class LoadProductCostItems(bpy.types.Operator):
    bl_idname = "bim.load_product_cost_items"
    bl_label = "Get Product Cost Assignments"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not tool.Ifc.get() or not (obj := context.active_object) or not (obj.BIMObjectProperties.ifc_definition_id):
            cls.poll_message_set("No IFC object is active.")
            return False
        return True

    def execute(self, context):
        core.load_product_cost_items(
            tool.Cost, product=tool.Ifc.get().by_id(context.active_object.BIMObjectProperties.ifc_definition_id)
        )
        return {"FINISHED"}


class HighlightProductCostItem(bpy.types.Operator):
    bl_idname = "bim.highlight_product_cost_item"
    bl_label = "Highlight Product Cost Items"
    bl_options = {"REGISTER", "UNDO"}
    cost_item: bpy.props.IntProperty()

    def execute(self, context):
        r = core.highlight_product_cost_item(tool.Spatial, tool.Cost, cost_item=tool.Ifc.get().by_id(self.cost_item))
        if isinstance(r, str):
            self.report({"WARNING"}, r)
        return {"FINISHED"}


class ReorderCostItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.reorder_cost_item_nesting"
    bl_label = "Reorder Nesting"
    bl_options = {"REGISTER", "UNDO"}
    new_index: bpy.props.IntProperty()
    cost_item: bpy.props.IntProperty()

    def _execute(self, context):
        ifcopenshell.api.run(
            "nest.reorder_nesting",
            tool.Ifc.get(),
            **{
                "item": tool.Ifc.get().by_id(self.cost_item),
                "new_index": self.new_index,
            },
        )
        tool.Cost.load_cost_schedule_tree()


class SelectUnassignedProducts(bpy.types.Operator):
    bl_idname = "bim.select_unassigned_products"
    bl_label = "Select Unassigned Products"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        core.select_unassigned_products(tool.Ifc, tool.Cost, tool.Spatial)
        return {"FINISHED"}


class ChangeParentCostItem(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.change_parent_cost_item"
    bl_label = "Change Parent Cost Item"
    bl_options = {"REGISTER", "UNDO"}
    new_parent: bpy.props.IntProperty()

    def _execute(self, context):
        r = core.change_parent_cost_item(tool.Ifc, tool.Cost, new_parent=tool.Ifc.get().by_id(self.new_parent))
        if isinstance(r, str):
            self.report({"WARNING"}, r)
        return {"FINISHED"}


class AddCurrency(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_currency"
    bl_label = "Add Currency"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        core.add_currency(tool.Ifc, tool.Cost)


class GenerateCostScheduleBrowser(bpy.types.Operator):
    bl_idname = "bim.generate_cost_schedule_browser"
    bl_label = "Generate Cost Schedule Browser"
    bl_options = {"REGISTER", "UNDO"}
    cost_schedule: bpy.props.IntProperty()

    def execute(self, context):
        core.generate_cost_schedule_browser(tool.Cost, cost_schedule=tool.Ifc.get().by_id(self.cost_schedule))
        return {"FINISHED"}
