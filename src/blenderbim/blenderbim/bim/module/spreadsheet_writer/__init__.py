import bpy 
from . import ui, prop, operator 

classes  = (

    prop.MyItem,
    prop.MyCollection,
    prop.BlenderBIMSpreadSheetProperties,
    operator.MyCollectionActions,
    operator.ConstructDataFrame,
    operator.WriteToXLSX,
    operator.WriteToODS,
    operator.FilterIFCElements,
    operator.UnhideIFCElements,
    ui.BlenderBIMSpreadSheet,
    ui.MyItem,
    ui.MyCollection,
    ui.MyCollectionActions
)

def register():

    bpy.utils.register_class(ui.MyItem)
    bpy.utils.register_class(ui.MyCollection)
    bpy.types.Scene.my_collection = bpy.props.PointerProperty(type=prop.MyCollection)
    bpy.utils.register_class(operator.MyCollectionActions) 
    bpy.utils.register_class(prop.BlenderBIMSpreadSheetProperties)
    bpy.types.Scene.blenderbim_spreadsheet_properties = bpy.props.PointerProperty(type=prop.BlenderBIMSpreadSheetProperties)     
    bpy.utils.register_class(operator.WriteToXLSX)
    bpy.utils.register_class(operator.WriteToODS) 
    bpy.utils.register_class(operator.FilterIFCElements)
    bpy.utils.register_class(operator.UnhideIFCElements)
    bpy.utils.register_class(ui.BlenderBIMSpreadSheet)
    
def unregister(): 
    
    bpy.utils.unregister_class(ui.MyItem)
    bpy.utils.unregister_class(ui.MyCollection)
    bpy.utils.unregister_class(operator.MyCollectionActions) 
    bpy.utils.unregister_class(prop.BlenderBIMSpreadSheetProperties)
    bpy.utils.unregister_class(operator.WriteToXLSX)
    bpy.utils.unregister_class(operator.WriteToODS)
    bpy.utils.unregister_class(operator.FilterIFCElements)
    bpy.utils.unregister_class(operator.UnhideIFCElements)
    bpy.utils.unregister_class(prop.BlenderBIMSpreadSheet)

