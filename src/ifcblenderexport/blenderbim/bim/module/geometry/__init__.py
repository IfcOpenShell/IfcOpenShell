import bpy
from . import ui, prop, operator

classes = (
    operator.EditObjectPlacement,
    operator.AddRepresentation,
    operator.MapRepresentations,
    operator.MapRepresentation,
    operator.SwitchRepresentation,
    operator.RemoveRepresentation,
    operator.UpdateMeshRepresentation,
    operator.UpdateParametricRepresentation,
    operator.GetRepresentationIfcParameters,
    prop.BIMGeometryProperties,
    ui.BIM_PT_representations,
    ui.BIM_PT_mesh,
    ui.BIM_PT_workarounds,
)


def register():
    bpy.types.Scene.BIMGeometryProperties = bpy.props.PointerProperty(type=prop.BIMGeometryProperties)
    bpy.types.OBJECT_PT_transform.append(ui.BIM_PT_transform)


def unregister():
    bpy.types.OBJECT_PT_transform.remove(ui.BIM_PT_transform)
    del bpy.types.Scene.BIMGeometryProperties
