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
    prop.StructuralAnalysisModel,
    prop.BIMStructuralProperties,
    ui.BIM_PT_structural,
    ui.BIM_UL_structural_analysis_models,
)


def register():
    bpy.types.Scene.BIMStructuralProperties = bpy.props.PointerProperty(type=prop.BIMStructuralProperties)


def unregister():
    del bpy.types.Scene.BIMStructuralProperties
