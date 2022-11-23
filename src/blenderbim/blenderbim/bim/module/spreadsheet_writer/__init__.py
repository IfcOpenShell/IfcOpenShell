
import bpy 
from . import ui, prop, operator 

classes  = (

    prop.MyItem,
    prop.MyCollection,
    operator.MyCollectionActions,
    operator.ConstructDataFrame,
    operator.WriteToXLSX,
    operator.WriteToODS,
    operator.FilterIFCElements,
    operator.UnhideIFCElements
)



"""  
def register():
    


    bpy.utils.register_class(MyItem)
    bpy.utils.register_class(MyCollection)
    bpy.types.Scene.my_collection = bpy.props.PointerProperty(type=MyCollection)
    bpy.utils.register_class(MyCollectionActions) 
    bpy.utils.register_class(BlenderBIMSpreadSheetProperties)
    bpy.types.Scene.blenderbim_spreadsheet_properties = bpy.props.PointerProperty(type=BlenderBIMSpreadSheetProperties)     
    bpy.utils.register_class(WriteToXLSX)
    bpy.utils.register_class(WriteToODS) 
    bpy.utils.register_class(FilterIFCElements)
    bpy.utils.register_class(UnhideIFCElements)
    bpy.utils.register_class(BlenderBIMSpreadSheetPanel)
    
def unregister(): 
    
    bpy.utils.unregister_class(MyItem)
    bpy.utils.unregister_class(MyCollection)
    bpy.utils.unregister_class(MyCollectionActions) 
    bpy.utils.unregister_class(BlenderBIMSpreadSheetProperties)
    bpy.utils.unregister_class(WriteToXLSX)
    bpy.utils.unregister_class(WriteToODS)
    bpy.utils.unregister_class(FilterIFCElements)
    bpy.utils.unregister_class(UnhideIFCElements)
    bpy.utils.unregister_class(BlenderBIMSpreadSheetPanel)



class MyItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Property",description="Use the PropertySet name and Property name divided by a .",default = "[PropertySet.Property]") 

class MyCollection(bpy.types.PropertyGroup):
    items: bpy.props.CollectionProperty(type=MyItem)

class MyCollectionActions(bpy.types.Operator):
    bl_idname = "my.collection_actions"
    bl_label = "Execute"
    action: bpy.props.EnumProperty(
        items=(
            ("add",) * 3,
            ("remove",) * 3,
        ),
    )
    def execute(self, context):
        my_collection = context.scene.my_collection
        if self.action == "add":           
            item = my_collection.items.add()  
        if self.action == "remove":
            my_collection.items.remove(len(my_collection.items) - 1)
        return {"FINISHED"}

def register():
    bpy.utils.register_class(MyItem)
    bpy.utils.register_class(MyCollection)
    bpy.types.Scene.my_collection = bpy.props.PointerProperty(type=MyCollection)
    bpy.utils.register_class(MyCollectionActions) 
    bpy.utils.register_class(BlenderBIMSpreadSheetProperties)
    bpy.types.Scene.blenderbim_spreadsheet_properties = bpy.props.PointerProperty(type=BlenderBIMSpreadSheetProperties)     
    bpy.utils.register_class(WriteToXLSX)
    bpy.utils.register_class(WriteToODS) 
    bpy.utils.register_class(FilterIFCElements)
    bpy.utils.register_class(UnhideIFCElements)
    bpy.utils.register_class(BlenderBIMSpreadSheetPanel)
    
def unregister(): 
    
    bpy.utils.unregister_class(MyItem)
    bpy.utils.unregister_class(MyCollection)
    bpy.utils.unregister_class(MyCollectionActions) 
    bpy.utils.unregister_class(BlenderBIMSpreadSheetProperties)
    bpy.utils.unregister_class(WriteToXLSX)
    bpy.utils.unregister_class(WriteToODS)
    bpy.utils.unregister_class(FilterIFCElements)
    bpy.utils.unregister_class(UnhideIFCElements)
    bpy.utils.unregister_class(BlenderBIMSpreadSheetPanel)
    
if __name__ == "__main__":
    register()

"""