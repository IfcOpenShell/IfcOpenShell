import bpy
from . import ui, operator

classes = (
    operator.TogglePsetExpansion,
    operator.EnablePsetEditing,
    operator.DisablePsetEditing,
    operator.EditPset,
    operator.RemovePset,
    operator.AddPset,
    ui.BIM_PT_object_psets,
)


def register():
    pass


def unregister():
    pass
