import bpy
from . import prop
from . import operator
from . import ui

classes = (
    prop.BIM_PT_existing_lods,
    prop.BIM_PT_ifccityjson_properties,
    operator.BIM_OT_cityjson2ifc,
    operator.BIM_OT_find_cityjson_lod,
    ui.BIM_PT_cityjson_converter,
)

def register():
    bpy.types.Scene.ifccityjson_properties = bpy.props.PointerProperty(type=prop.BIM_PT_ifccityjson_properties)

def unregister():
    del bpy.types.Scene.ifccityjson_properties