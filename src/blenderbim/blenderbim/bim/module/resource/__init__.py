import bpy
from . import ui, prop, operator

classes = (
    operator.DisableResourceEditingUI,
    operator.DisableEditingResource,
    operator.EnableEditingResource,
    operator.LoadResources,
    operator.AddResource,
    operator.EditResource,
    operator.RemoveResource,
    operator.LoadResourceProperties,
    operator.ExpandResource,
    operator.ContractResource,
    operator.AssignResource,
    operator.UnassignResource,
    prop.Resource,
    prop.BIMResourceProperties,
    prop.BIMResourceTreeProperties,
    ui.BIM_PT_resources,
    ui.BIM_UL_resources,
)


def register():
    bpy.types.Scene.BIMResourceProperties = bpy.props.PointerProperty(type=prop.BIMResourceProperties)
    bpy.types.Scene.BIMResourceTreeProperties = bpy.props.PointerProperty(type=prop.BIMResourceTreeProperties)

def unregister():
    del bpy.types.Scene.BIMResourceProperties
    del bpy.types.Scene.BIMResourceTreeProperties
