import bpy
from . import ui, prop, operator

classes = (
    operator.DisableResourceEditingUI,
    operator.DisableEditingResource,
    operator.EnableEditingResource,
    operator.LoadResources,
    operator.AddCrewResource,
    operator.AddSubcontractResource,
    operator.EditResource,
    operator.RemoveResource,
    prop.Resource,
    prop.BIMResourceProperties,
    ui.BIM_PT_resources,
    ui.BIM_UL_resources,
)


def register():
    bpy.types.Scene.BIMResourceProperties = bpy.props.PointerProperty(type=prop.BIMResourceProperties)

def unregister():
    del bpy.types.Scene.BIMResourceProperties
