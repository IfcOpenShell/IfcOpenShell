import bpy
from bpy.types import Panel 
from blenderbim.bim.ifc import IfcStore
from . import operator



class BlenderBIMSpreadSheetPanel(Panel):
    """Creates a Panel in the Object properties window"""  

    bl_idname = "BlenderBIMSpreadSheetPanel"  # this is not strictly necessary
    bl_label = "BlenderBIM spreadsheet"
    
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlenderBIM"
 
    def draw(self, context):
        
        layout = self.layout
        blenderbim_spreadsheet_properties = context.scene.blenderbim_spreadsheet_properties
        
        layout.label(text="General")
        box = layout.box()
        row = box.row()
        row.prop(blenderbim_spreadsheet_properties, "my_ifcproduct")
        row = box.row()
        row.prop(blenderbim_spreadsheet_properties, "my_ifcbuildingstorey")
        row = box.row()
        row.prop(blenderbim_spreadsheet_properties, "my_ifcproduct_name")
        row = box.row()
        row.prop(blenderbim_spreadsheet_properties, "my_type")
        row = box.row()
        row.prop(blenderbim_spreadsheet_properties, "my_ifcclassification")
        row = box.row()
        row.prop(blenderbim_spreadsheet_properties, "my_ifcmaterial")
        
        layout.label(text="Common Properties")
        box = layout.box()
        row = box.row()
        row.prop(blenderbim_spreadsheet_properties, "my_isexternal")
        row = box.row()
        row.prop(blenderbim_spreadsheet_properties, "my_loadbearing")
        row = box.row()
        row.prop(blenderbim_spreadsheet_properties, "my_firerating")
        
        layout.label(text="BaseQuantities")
        box = layout.box()
        row = box.row()
        row.prop(blenderbim_spreadsheet_properties, "my_length")
        row = box.row()
        row.prop(blenderbim_spreadsheet_properties, "my_width")
        row = box.row()
        row.prop(blenderbim_spreadsheet_properties, "my_height")
        row = box.row()
        row.prop(blenderbim_spreadsheet_properties, "my_area")
        row = box.row()
        row.prop(blenderbim_spreadsheet_properties, "my_netarea")
        row = box.row()
        row.prop(blenderbim_spreadsheet_properties, "my_netsidearea")
        row = box.row()
        row.prop(blenderbim_spreadsheet_properties, "my_volume")
        row = box.row()
        row.prop(blenderbim_spreadsheet_properties, "my_netvolume")
        row = box.row()
        row.prop(blenderbim_spreadsheet_properties, "my_perimeter")
        
        layout.label(text="Custom Properties")
        my_collection = context.scene.my_collection
       
        row = layout.row(align=True)
        row.operator("my.collection_actions", text="Add", icon="ADD").action = "add"
        row.operator("my.collection_actions", text="Remove Last", icon="REMOVE").action = "remove"

        for item in my_collection.items:
            layout.prop(item, "name")
        
        layout.label(text="Write to spreadsheet")
        self.layout.operator(operator.WriteToXLSX.bl_idname, text="Write IFC data to .xlsx", icon="FILE")
        self.layout.operator(operator.WriteToODS.bl_idname, text="Write IFC data to .ods", icon="FILE")
        
        layout.label(text="Filter IFC elements")
  
        box = layout.box()
        row = box.row()
        row.prop(blenderbim_spreadsheet_properties, "my_file_path")
        self.layout.operator(operator.FilterIFCElements.bl_idname, text="Filter IFC elements", icon="FILTER")
        self.layout.operator(operator.UnhideIFCElements.bl_idname, text="Unhide IFC elements", icon="LIGHT")

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