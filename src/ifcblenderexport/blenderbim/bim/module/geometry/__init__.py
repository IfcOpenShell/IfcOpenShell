import bpy
from . import ui, operator

classes = (
    operator.EditObjectPlacement,
    operator.AddRepresentation,
    operator.SwitchRepresentation,
    operator.RemoveRepresentation,
    operator.UpdateMeshRepresentation,
    operator.UpdateParametricRepresentation,
    operator.GetRepresentationIfcParameters,
    ui.BIM_PT_representations,
    ui.BIM_PT_mesh,
)


def register():
    bpy.types.OBJECT_PT_transform.append(ui.BIM_PT_transform)


def unregister():
    bpy.types.OBJECT_PT_transform.remove(ui.BIM_PT_transform)
