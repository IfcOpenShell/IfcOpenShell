import bpy
from . import ui, prop, operator

classes = (
    operator.LoadProfiles,
    operator.DisableProfileEditingUI,
    operator.RemoveProfileDef,
    operator.EnableEditingProfile,
    operator.DisableEditingProfile,
    operator.EditProfile,
    prop.Profile,
    prop.BIMProfileProperties,
    ui.BIM_PT_profiles,
    ui.BIM_UL_profiles,
)


def register():
    bpy.types.Scene.BIMProfileProperties = bpy.props.PointerProperty(type=prop.BIMProfileProperties)


def unregister():
    del bpy.types.Scene.BIMProfileProperties
