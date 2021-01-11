import bpy
from . import ui, operator

classes = (
    operator.SelectCobieIfcFile,
    operator.SelectCobieJsonFile,
    operator.ExecuteIfcCobie,
    ui.BIM_PT_cobie,
)


def register():
    pass


def unregister():
    pass
