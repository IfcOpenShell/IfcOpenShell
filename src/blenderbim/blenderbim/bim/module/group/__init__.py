import bpy
from . import ui, prop, operator

classes = (
    operator.LoadGroups,
    operator.DisableGroupEditingUI,
    operator.AddGroup,
    operator.EditGroup,
    operator.RemoveGroup,
    operator.AssignGroup,
    operator.UnassignGroup,
    operator.EnableEditingGroup,
    operator.DisableEditingGroup,
    prop.Group,
    prop.BIMGroupProperties,
    ui.BIM_PT_groups,
    ui.BIM_UL_groups,
)


def register():
    bpy.types.Scene.BIMGroupProperties = bpy.props.PointerProperty(type=prop.BIMGroupProperties)


def unregister():
    del bpy.types.Scene.BIMGroupProperties
