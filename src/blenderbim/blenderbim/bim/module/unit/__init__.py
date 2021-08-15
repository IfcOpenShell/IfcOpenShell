import bpy
from . import ui, prop, operator

classes = (
    operator.AssignUnit,
    operator.UnassignUnit,
    operator.LoadUnits,
    operator.DisableUnitEditingUI,
    operator.RemoveUnit,
    operator.AddMonetaryUnit,
    operator.AddSIUnit,
    operator.EnableEditingUnit,
    operator.DisableEditingUnit,
    operator.EditUnit,
    prop.Unit,
    prop.BIMUnitProperties,
    ui.BIM_PT_units,
    ui.BIM_UL_units,
)


def register():
    bpy.types.Scene.BIMUnitProperties = bpy.props.PointerProperty(type=prop.BIMUnitProperties)


def unregister():
    del bpy.types.Scene.BIMUnitProperties
