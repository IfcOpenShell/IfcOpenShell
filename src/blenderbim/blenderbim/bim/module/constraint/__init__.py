import bpy
from . import ui, prop, operator

classes = (
    operator.LoadObjectives,
    operator.DisableConstraintEditingUI,
    operator.EnableEditingConstraint,
    operator.DisableEditingConstraint,
    operator.AddObjective,
    operator.EditObjective,
    operator.RemoveConstraint,
    operator.EnableAssigningConstraint,
    operator.DisableAssigningConstraint,
    operator.AssignConstraint,
    operator.UnassignConstraint,
    prop.Constraint,
    prop.BIMConstraintProperties,
    prop.BIMObjectConstraintProperties,
    ui.BIM_PT_constraints,
    ui.BIM_PT_object_constraints,
    ui.BIM_UL_constraints,
    ui.BIM_UL_object_constraints,
)


def register():
    bpy.types.Scene.BIMConstraintProperties = bpy.props.PointerProperty(type=prop.BIMConstraintProperties)
    bpy.types.Object.BIMObjectConstraintProperties = bpy.props.PointerProperty(type=prop.BIMObjectConstraintProperties)


def unregister():
    del bpy.types.Scene.BIMConstraintProperties
    del bpy.types.Object.BIMObjectConstraintProperties
