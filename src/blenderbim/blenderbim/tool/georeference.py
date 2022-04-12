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


import bpy
import json
import blenderbim.core.tool
import blenderbim.tool as tool
import ifcopenshell

from ifcopenshell.api.unit.data import Data as UnitData

class Georeference(blenderbim.core.tool.Georeference):
    
    @classmethod
    def clear_projected_crs(cls):
        bpy.context.scene.BIMGeoreferenceProperties.projected_crs.clear()
    
    @classmethod
    def clear_map_conversion(cls):
        bpy.context.scene.BIMGeoreferenceProperties.map_conversion.clear()
    
    @classmethod
    def get_file(cls):
        return tool.Ifc.get()
    
    @classmethod
    def import_projected_crs_attributes(cls, name, prop, data):
        if name == "MapUnit":
            new = bpy.context.scene.BIMGeoreferenceProperties.projected_crs.add()
            new.name = name
            new.data_type = "enum"
            new.is_null = data[name] is None
            new.is_optional = True
            new.enum_items = json.dumps(
                {u["id"]: u["Name"] for u in UnitData.units.values() if u["UnitType"] == "LENGTHUNIT"}
            )
            if data["MapUnit"]:
                new.enum_value = str(data["MapUnit"]["id"])
            return True
    
    @classmethod
    def import_map_conversion_attributes(cls, name, prop, data):
        if name not in ["SourceCRS", "TargetCRS"]:
            # Enforce a string data type to prevent data loss in single-precision Blender props
            prop.data_type = "string"
            prop.string_value = "" if prop.is_null else str(data[name])
            return True
    
    @classmethod
    def export_crs_attributes(cls, attributes, prop,):
        ifc_file = tool.Ifc.get()
        if not prop.is_null and prop.name == "MapUnit":
            attributes[prop.name] = ifc_file.by_id(int(prop.enum_value))
            return True
    
    @classmethod        
    def export_map_attributes(cls, attributes, prop):
        if not prop.is_null and prop.data_type == "string":
            # We store our floats as string to prevent single precision data loss
            attributes[prop.name] = float(prop.string_value)
            return True
    
    @classmethod
    def set_false_is_editing(cls):
        props = bpy.context.scene.BIMGeoreferenceProperties
        props.is_editing = False
    
    @classmethod
    def set_ifc_grid_north(cls):
        x_angle = -bpy.context.scene.sun_pos_properties.north_offset
        bpy.context.scene.BIMGeoreferenceProperties.map_conversion.get("XAxisAbscissa").string_value = str(cos(x_angle))
        bpy.context.scene.BIMGeoreferenceProperties.map_conversion.get("XAxisOrdinate").string_value = str(sin(x_angle))
    
    @classmethod
    def set_blender_grid_north(cls):
        bpy.context.scene.sun_pos_properties.north_offset = -radians(
            ifcopenshell.util.geolocation.xaxis2angle(
                float(bpy.context.scene.BIMGeoreferenceProperties.map_conversion.get("XAxisAbscissa").string_value),
                float(bpy.context.scene.BIMGeoreferenceProperties.map_conversion.get("XAxisOrdinate").string_value),
            )
        )
    

