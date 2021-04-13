import bpy
from . import ui, prop, operator

classes = (
    operator.LoadStructuralAnalysisModels,
    operator.DisableStructuralAnalysisModelEditingUI,
    operator.AddStructuralAnalysisModel,
    operator.EditStructuralAnalysisModel,
    operator.RemoveStructuralAnalysisModel,
    operator.AssignStructuralAnalysisModel,
    operator.UnassignStructuralAnalysisModel,
    operator.EnableEditingStructuralAnalysisModel,
    operator.DisableEditingStructuralAnalysisModel,
    operator.AddStructuralBoundaryCondition,
    operator.EditStructuralBoundaryCondition,
    operator.RemoveStructuralBoundaryCondition,
    operator.EnableEditingStructuralBoundaryCondition,
    operator.DisableEditingStructuralBoundaryCondition,
    operator.AddStructuralMemberConnection,
    operator.EnableEditingStructuralConnectionCondition,
    operator.DisableEditingStructuralConnectionCondition,
    operator.RemoveStructuralConnectionCondition,
    operator.EnableEditingStructuralMemberAxis,
    operator.DisableEditingStructuralMemberAxis,
    operator.EditStructuralMemberAxis,
    prop.StructuralAnalysisModel,
    prop.BIMStructuralProperties,
    prop.BIMObjectStructuralProperties,
    ui.BIM_PT_structural_analysis_models,
    ui.BIM_PT_structural_boundary_conditions,
    ui.BIM_PT_connected_structural_members,
    ui.BIM_PT_structural_member,
    ui.BIM_UL_structural_analysis_models,
)


def register():
    bpy.types.Scene.BIMStructuralProperties = bpy.props.PointerProperty(type=prop.BIMStructuralProperties)
    bpy.types.Object.BIMStructuralProperties = bpy.props.PointerProperty(type=prop.BIMObjectStructuralProperties)


def unregister():
    del bpy.types.Scene.BIMStructuralProperties
    del bpy.types.Object.BIMStructuralProperties
