import bpy
from . import ui, operator

classes = (
    operator.AddRepresentation,
    operator.SwitchRepresentation,
    operator.RemoveRepresentation,
    operator.BakeParametricGeometry,
    operator.UpdateIfcRepresentation,
    operator.GetRepresentationIfcParameters,
    ui.BIM_PT_representations,
)


def register():
    pass


def unregister():
    pass
