import bpy
from . import ui, prop, operator

classes = (
    operator.EnableEditingGeoreferencing,
    operator.DisableEditingGeoreferencing,
    operator.EditGeoreferencing,
    operator.SetNorthOffset,
    operator.GetNorthOffset,
    operator.RemoveGeoreferencing,
    operator.AddGeoreferencing,
    operator.ConvertLocalToGlobal,
    operator.ConvertGlobalToLocal,
    operator.GetCursorLocation,
    operator.SetCursorLocation,
    prop.BIMGeoreferenceProperties,
    ui.BIM_PT_gis,
    ui.BIM_PT_gis_utilities,
)


def register():
    bpy.types.Scene.BIMGeoreferenceProperties = bpy.props.PointerProperty(type=prop.BIMGeoreferenceProperties)


def unregister():
    del bpy.types.Scene.BIMGeoreferenceProperties
