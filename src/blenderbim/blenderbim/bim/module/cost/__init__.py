import bpy
from . import ui, prop, operator

classes = (
    operator.AddCostSchedule,
    operator.RemoveCostSchedule,
    operator.EditCostSchedule,
    operator.EditCostItem,
    operator.EditCostItemQuantity,
    operator.EditCostValue,
    operator.EnableEditingCostSchedule,
    operator.EnableEditingCostItems,
    operator.EnableEditingCostItem,
    operator.EnableEditingCostItemQuantities,
    operator.EnableEditingCostItemQuantity,
    operator.EnableEditingCostItemValues,
    operator.EnableEditingCostItemValue,
    operator.DisableEditingCostItem,
    operator.DisableEditingCostSchedule,
    operator.DisableEditingCostItemQuantity,
    operator.DisableEditingCostItemValue,
    operator.AddCostItem,
    operator.AddSummaryCostItem,
    operator.ExpandCostItem,
    operator.ContractCostItem,
    operator.RemoveCostItem,
    operator.AssignCostItemProduct,
    operator.UnassignCostItemProduct,
    operator.AddCostItemQuantity,
    operator.RemoveCostItemQuantity,
    operator.AddCostValue,
    operator.RemoveCostItemValue,
    operator.CopyCostItemValues,
    operator.SelectCostItemProducts,
    operator.SelectCostScheduleProducts,
    prop.CostItem,
    prop.BIMCostProperties,
    ui.BIM_PT_cost_schedules,
    ui.BIM_UL_cost_items,
)


def register():
    bpy.types.Scene.BIMCostProperties = bpy.props.PointerProperty(type=prop.BIMCostProperties)


def unregister():
    del bpy.types.Scene.BIMCostProperties
