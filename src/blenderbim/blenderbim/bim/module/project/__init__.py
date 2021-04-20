import bpy
from . import ui, prop, operator

classes = (
    operator.CreateProject,
    operator.CreateProjectLibrary,
    operator.ValidateIfcFile,
    operator.SelectLibraryFile,
    operator.ChangeLibraryElement,
    operator.RefreshLibrary,
    operator.RewindLibrary,
    prop.LibraryElement,
    prop.BIMProjectProperties,
    ui.BIM_PT_project,
    ui.BIM_PT_project_library,
    ui.BIM_UL_library,
)


def register():
    bpy.types.Scene.BIMProjectProperties = bpy.props.PointerProperty(type=prop.BIMProjectProperties)


def unregister():
    del bpy.types.Scene.BIMProjectProperties
