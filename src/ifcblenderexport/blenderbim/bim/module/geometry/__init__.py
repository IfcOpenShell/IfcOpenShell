import bpy
from . import ui, operator

classes = (
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
    pass


def unregister():
    pass
