import bpy
from . import ui, prop, operator

classes = (
    operator.LoadLayers,
    operator.DisableLayerEditingUI,
    operator.EnableEditingLayer,
    operator.DisableEditingLayer,
    operator.AddPresentationLayer,
    operator.EditPresentationLayer,
    operator.RemovePresentationLayer,
    operator.AssignPresentationLayer,
    operator.UnassignPresentationLayer,
    prop.Layer,
    prop.BIMLayerProperties,
    ui.BIM_PT_layers,
    ui.BIM_UL_layers,
)


def register():
    bpy.types.Scene.BIMLayerProperties = bpy.props.PointerProperty(type=prop.BIMLayerProperties)


def unregister():
    del bpy.types.Scene.BIMLayerProperties
