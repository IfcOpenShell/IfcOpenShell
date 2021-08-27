
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

import bpy
from . import ui, prop, operator

classes = (
    operator.AddCostSchedule,
    operator.RemoveCostSchedule,
    operator.EditCostSchedule,
    operator.EditCostItem,
    operator.EditCostItemQuantity,
    operator.EditCostItemValue,
    operator.EditCostItemValueFormula,
    operator.EnableEditingCostSchedule,
    operator.EnableEditingCostItems,
    operator.EnableEditingCostItem,
    operator.EnableEditingCostItemQuantities,
    operator.EnableEditingCostItemQuantity,
    operator.EnableEditingCostItemValues,
    operator.EnableEditingCostItemValue,
    operator.EnableEditingCostItemValueFormula,
    operator.DisableEditingCostItem,
    operator.DisableEditingCostSchedule,
    operator.DisableEditingCostItemQuantity,
    operator.DisableEditingCostItemValue,
    operator.AddCostColumn,
    operator.RemoveCostColumn,
    operator.AddCostItem,
    operator.AddSummaryCostItem,
    operator.ExpandCostItem,
    operator.ContractCostItem,
    operator.RemoveCostItem,
    operator.AssignCostItemType,
    operator.UnassignCostItemType,
    operator.AssignCostItemQuantity,
    operator.UnassignCostItemQuantity,
    operator.AddCostItemQuantity,
    operator.RemoveCostItemQuantity,
    operator.AddCostValue,
    operator.RemoveCostItemValue,
    operator.CopyCostItemValues,
    operator.SelectCostItemProducts,
    operator.SelectCostScheduleProducts,
    operator.ImportCostScheduleCsv,
    operator.LoadCostItemQuantities,
    operator.LoadCostItemTypes,
    operator.AssignCostValue,
    operator.LoadScheduleOfRates,
    operator.ExpandCostItemRate,
    operator.ContractCostItemRate,
    prop.CostItem,
    prop.CostItemQuantity,
    prop.CostItemType,
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
)


def menu_func_import(self, context):
    self.layout.operator(operator.ImportCostScheduleCsv.bl_idname, text="Cost Schedule (.csv)")


def register():
    bpy.types.Scene.BIMCostProperties = bpy.props.PointerProperty(type=prop.BIMCostProperties)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    del bpy.types.Scene.BIMCostProperties
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
