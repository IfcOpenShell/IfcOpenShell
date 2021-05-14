import bpy
from . import ui, prop, operator

classes = (
    operator.AssignContainer,
    operator.RemoveContainer,
    operator.EnableEditingContainer,
    operator.DisableEditingContainer,
    operator.ChangeSpatialLevel,
    prop.SpatialElement,
    prop.BIMSpatialProperties,
    prop.BIMObjectSpatialProperties,
    ui.BIM_PT_spatial,
    ui.BIM_UL_spatial_elements,
)


def register():
    bpy.types.Scene.BIMSpatialProperties = bpy.props.PointerProperty(type=prop.BIMSpatialProperties)
    bpy.types.Object.BIMObjectSpatialProperties = bpy.props.PointerProperty(type=prop.BIMObjectSpatialProperties)


def unregister():
    del bpy.types.Scene.BIMSpatialProperties
    del bpy.types.Object.BIMObjectSpatialProperties
