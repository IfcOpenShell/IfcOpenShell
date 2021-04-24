import bpy
from . import ui, prop, operator

classes = (
    operator.DisableResourceEditingUI,
    operator.DisableEditingResource,
    operator.EnableEditingResource,
    operator.LoadResources,
    operator.AddCrewResource,
    operator.AddSubcontractResource,
    operator.AddEquipementResource,
    operator.AddLaborResource,
    operator.AddProductResource,
    operator.AddMaterialResource,
    operator.EditResource,
    operator.RemoveResource,
    operator.EnableEditingNestedResource,
    operator.LoadNestedResourceProperties,
    operator.DisableNestedResourceEditingUI,
    prop.Resource,
    prop.BIMResourceProperties,
    prop.BIMResourceTreeProperties,
    ui.BIM_PT_resources,
    ui.BIM_UL_nested_resources,
)


def register():
    bpy.types.Scene.BIMResourceProperties = bpy.props.PointerProperty(type=prop.BIMResourceProperties)
    bpy.types.Scene.BIMResourceTreeProperties = bpy.props.PointerProperty(type=prop.BIMResourceTreeProperties)

def unregister():
    del bpy.types.Scene.BIMResourceProperties
    del bpy.types.Scene.BIMResourceTreeProperties
