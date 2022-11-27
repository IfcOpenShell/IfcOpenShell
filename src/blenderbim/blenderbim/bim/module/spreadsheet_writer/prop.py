import os
import sys
import time
import site
import collections
import subprocess

site.addsitedir(os.path.join(os.path.dirname(os.path.realpath(__file__)), "libs", "site", "packages"))

import bpy
from bpy.props import StringProperty, BoolProperty, IntProperty, EnumProperty
from bpy_extras.io_utils import ImportHelper 
from bpy.types import (Operator, PropertyGroup)




        
class BlenderBIMSpreadSheetProperties(bpy.types.PropertyGroup):
    ###############################################
    ################# General #####################
    ############################################### 
    my_ifcproduct: bpy.props.BoolProperty(name="IfcProduct",description="Export IfcProduct",default=True)
    my_ifcbuildingstorey: bpy.props.BoolProperty(name="IfcBuildingStorey",description="Export IfcBuildingStorey",default = True)     
    my_ifcproduct_name: bpy.props.BoolProperty(name="Name",description="Export IfcProduct Name",default = True)
    my_type: bpy.props.BoolProperty(name="Type",description="Export IfcObjectType Name",default = True)
    my_ifcclassification: bpy.props.BoolProperty(name="IfcClassification",description="Export Classification",default = True)
    my_ifcmaterial: bpy.props.BoolProperty(name="IfcMaterial",description="Export Materials",default = True)
     
    ###############################################
    ############ Common Properties ################
    ###############################################
    my_isexternal: bpy.props.BoolProperty(name="IsExternal",description="Export IsExternal",default = True)
    my_loadbearing: bpy.props.BoolProperty(name="LoadBearing",description="Export LoadBearing",default = True)
    my_firerating: bpy.props.BoolProperty(name="FireRating",description="Export FireRating",default = True)
    
    ###############################################
    ############# BaseQuantities ##################
    ###############################################
    my_length: bpy.props.BoolProperty(name="Length",description="Export Length from BaseQuantities",default = True)  
    my_width: bpy.props.BoolProperty(name="Width",description="Export Width from BaseQuantities",default = True)   
    my_height: bpy.props.BoolProperty(name="Height",description="Export Height from BaseQuantities",default = True) 
   
    my_area: bpy.props.BoolProperty(name="Area",description="Gets each possible defintion of Area",default = True)  
    my_netarea: bpy.props.BoolProperty(name="NetArea",description="Export NetArea from BaseQuantities",default = True)
    my_netsidearea: bpy.props.BoolProperty(name="NetSideArea",description="Export NetSideArea from BaseQuantities",default = True)
    
    my_volume: bpy.props.BoolProperty(name="Volume",description="Export Volume from BaseQuantities",default = True) 
    my_netvolume: bpy.props.BoolProperty(name="NetVolume",description="Export NetVolume from BaseQuantities",default = True)
    
    my_perimeter: bpy.props.BoolProperty(name="Perimeter",description="Export Perimeter from BaseQuantities",default = True)      
  
    ###############################################
    ####### Spreadsheet Properties ################
    ###############################################
    my_workbook: bpy.props.StringProperty(name="my_workbook")
    my_xlsx_file: bpy.props.StringProperty(name="my_xlsx_file")
    my_ods_file: bpy.props.StringProperty(name="my_ods_file")
    
    my_file_path: bpy.props.StringProperty(name="Spreadsheet",
                                        description="your .ods or .xlsx file",
                                        default="",
                                        maxlen=1024,
                                        subtype="FILE_PATH")

    
class MyItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Property",description="Use the PropertySet name and Property name divided by a .",default = "[PropertySet.Property]") 

class MyCollection(bpy.types.PropertyGroup):
    items: bpy.props.CollectionProperty(type=MyItem)
