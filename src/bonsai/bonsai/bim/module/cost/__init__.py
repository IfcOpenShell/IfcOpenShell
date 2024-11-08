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
from . import ui, prop, operator

classes = (
    operator.AddCostColumn,
    operator.AddCostItem,
    operator.AddCostItemQuantity,
    operator.AddCostSchedule,
    operator.AddCostValue,
    operator.AddCurrency,
    operator.AddSummaryCostItem,
    operator.AssignCostItemQuantity,
    operator.AssignCostItemType,
    operator.AssignCostValue,
    operator.CalculateCostItemResourceValue,
    operator.ChangeParentCostItem,
    operator.ClearCostItemAssignments,
    operator.ContractCostItem,
    operator.ContractCostItemRate,
    operator.ContractCostItems,
    operator.CopyCostItem,
    operator.CopyCostItemValues,
    operator.DisableEditingCostItem,
    operator.DisableEditingCostItemQuantity,
    operator.DisableEditingCostItemValue,
    operator.DisableEditingCostSchedule,
    operator.EditCostItem,
    operator.EditCostItemQuantity,
    operator.EditCostItemValue,
    operator.EditCostItemValueFormula,
    operator.EditCostSchedule,
    operator.EnableEditingCostItem,
    operator.EnableEditingCostItemQuantities,
    operator.EnableEditingCostItemQuantity,
    operator.EnableEditingCostItems,
    operator.EnableEditingCostItemValue,
    operator.EnableEditingCostItemValueFormula,
    operator.EnableEditingCostItemValues,
    operator.EnableEditingCostSchedule,
    operator.ExpandCostItem,
    operator.ExpandCostItemRate,
    operator.ExpandCostItems,
    operator.ExportCostSchedules,
    operator.HighlightProductCostItem,
    operator.ImportCostScheduleCsv,
    operator.LoadCostItemElementQuantities,
    operator.LoadCostItemQuantities,
    operator.LoadCostItemResourceQuantities,
    operator.LoadCostItemTaskQuantities,
    operator.LoadCostItemTypes,
    operator.LoadProductCostItems,
    operator.LoadScheduleOfRates,
    operator.RemoveCostColumn,
    operator.RemoveCostItem,
    operator.RemoveCostItemQuantity,
    operator.RemoveCostItemValue,
    operator.RemoveCostSchedule,
    operator.ReorderCostItem,
    operator.SelectCostItemProducts,
    operator.SelectCostScheduleProducts,
    operator.SelectUnassignedProducts,
    operator.UnassignCostItemQuantity,
    operator.UnassignCostItemType,
    operator.GenerateCostScheduleBrowser,
    prop.CostItem,
    prop.CostItemQuantity,
    prop.CostItemType,
    prop.ScheduleColumn,
    prop.BIMCostProperties,
    ui.BIM_PT_cost_schedules,
    ui.BIM_PT_cost_item_quantities,
    ui.BIM_PT_cost_item_types,
    ui.BIM_PT_cost_item_rates,
    ui.BIM_UL_cost_items,
    ui.BIM_UL_cost_columns,
    ui.BIM_UL_cost_item_quantities,
    ui.BIM_UL_cost_item_types,
    ui.BIM_UL_cost_item_rates,
    ui.BIM_UL_product_cost_items,
    ui.BIM_PT_Costing_Tools,
)


def menu_func_import(self, context):
    self.layout.operator(operator.ImportCostScheduleCsv.bl_idname, text="Cost Schedule (.csv)")


def register():
    bpy.types.Scene.BIMCostProperties = bpy.props.PointerProperty(type=prop.BIMCostProperties)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    del bpy.types.Scene.BIMCostProperties
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
