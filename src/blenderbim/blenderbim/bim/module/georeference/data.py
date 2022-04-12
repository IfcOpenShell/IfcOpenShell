# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import blenderbim.tool as tool

def refresh():
    GeoreferenceData.is_loaded = False
    
class GeoreferenceData:
    data = {}
    is_loaded = False
    
    @classmethod
    def load(cls):         
        cls.data = {
            "map_conversion" : cls.map_conversion(),
            "projected_crs" : cls.projected_crs(),
            "true_north" : cls.true_north(),
        }
        cls.is_loaded = True
        
    @classmethod
    def map_conversion(cls):
        ifc = tool.Ifc.get()
        map_conversion_v = {}
        
        if ifc.schema == "IFC2X3":
            return
        
        for context in ifc.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if not context.HasCoordinateOperation:
                continue
            
            map_conversion_v = context.HasCoordinateOperation[0].get_info()
            map_conversion_v["SourceCRS"] = map_conversion_v["SourceCRS"].id()
            map_conversion_v["TargetCRS"] = map_conversion_v["TargetCRS"].id()
            
            break
        
        return map_conversion_v
            
    @classmethod
    def projected_crs(cls):
        ifc = tool.Ifc.get()
        projected_crs = {}
        
        if ifc.schema == "IFC2X3":
            return
        
        for context in ifc.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if not context.HasCoordinateOperation:
                continue
            
            projected_crs = context.HasCoordinateOperation[0].TargetCRS.get_info()
            if projected_crs["MapUnit"]:
                projected_crs["MapUnit"] = map_conversion.TargetCRS.MapUnit.get_info()

            break
        
        return projected_crs
     
    @classmethod
    def true_north(cls):
        ifc = tool.Ifc.get()
        true_north = {}
        
        if ifc.schema == "IFC2X3":
            return
             
        for context in ifc.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if not context.TrueNorth:
                continue
            true_north = context.TrueNorth.DirectionRatios
            break
        
        return true_north

