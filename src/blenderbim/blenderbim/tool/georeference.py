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
import blenderbim.bim.helper

from ifcopenshell.api.unit.data import Data as UnitData
from math import radians, degrees, atan, tan, cos, sin

class Georeference(blenderbim.core.tool.Georeference):
    
    @classmethod
    def clear_projected_crs(cls):
        bpy.context.scene.BIMGeoreferenceProperties.projected_crs.clear()
    
    @classmethod
    def clear_map_conversion(cls):
        bpy.context.scene.BIMGeoreferenceProperties.map_conversion.clear()
        
    @classmethod
    def import_projected_crs(cls):
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
        
        props = bpy.context.scene.BIMGeoreferenceProperties
        blenderbim.bim.helper.import_attributes(
            "IfcProjectedCRS",
            props.projected_crs,
            projected_crs,
            cls.import_projected_crs_attributes,
        )
    
    @classmethod
    def import_map_conversion(cls):
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
        
        props = bpy.context.scene.BIMGeoreferenceProperties
        blenderbim.bim.helper.import_attributes(
            "IfcMapConversion",
            props.map_conversion,
            map_conversion_v,
            cls.import_map_conversion_attributes,
        )        
    
    @classmethod
    def set_has_true_north_prop(cls):
        ifc = tool.Ifc.get()
        true_north = {}
        
        if ifc.schema == "IFC2X3":
            return
             
        for context in ifc.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if not context.TrueNorth:
                continue
            true_north = context.TrueNorth.DirectionRatios
            break

        bpy.context.scene.BIMGeoreferenceProperties.has_true_north = bool(true_north)
    
    @classmethod
    def set_true_north_props(cls):
        ifc = tool.Ifc.get()
        true_north = {}
        
        if ifc.schema == "IFC2X3":
            return
             
        for context in ifc.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if not context.TrueNorth:
                continue
            true_north = context.TrueNorth.DirectionRatios
            break
        
        if true_north:
            bpy.context.scene.BIMGeoreferenceProperties.true_north_abscissa = str(true_north[0])
            bpy.context.scene.BIMGeoreferenceProperties.true_north_ordinate = str(true_north[1])
    
    @classmethod
    def get_projected_crs_attributes(cls):
        props = bpy.context.scene.BIMGeoreferenceProperties
        projected_crs = blenderbim.bim.helper.export_attributes(props.projected_crs, cls.export_crs_attributes)
        return projected_crs
    
    @classmethod
    def get_map_conversion_attributes(cls):
        props = bpy.context.scene.BIMGeoreferenceProperties
        map_conversion = blenderbim.bim.helper.export_attributes(props.map_conversion, cls.export_map_attributes)
        return map_conversion
    
    @classmethod
    def get_true_north_attributes(cls):
        props = bpy.context.scene.BIMGeoreferenceProperties
        true_north = None
        if props.has_true_north:
            try:
                true_north = [float(props.true_north_abscissa), float(props.true_north_ordinate)]
            except ValueError:
                print("ERROR, True North Abscissa and Ordinate expect a number")
                #self.report({"ERROR"}, "True North Abscissa and Ordinate expect a number")
        return true_north
    
    @classmethod
    def enable_editing(cls):
        bpy.context.scene.BIMGeoreferenceProperties.is_editing = True
    
    @classmethod
    def disable_editing(cls):
        bpy.context.scene.BIMGeoreferenceProperties.is_editing = False
    
    @classmethod
    def edit_georeferencing(cls, projected_crs, map_conversion, true_north):
        tool.Ifc.run(
            "georeference.edit_georeferencing",
            **{
                "projected_crs": projected_crs,
                "map_conversion": map_conversion,
                "true_north": true_north,
            }
        )
    
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
    def export_crs_attributes(cls, attributes, prop):
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
    def get_cursor_location(cls):
        props = bpy.context.scene.BIMGeoreferenceProperties
        scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        project_coordinates = [o / scale for o in bpy.context.scene.cursor.location]
        props.coordinate_input = ",".join([str(o) for o in project_coordinates])
        
    @classmethod
    def set_cursor_location(cls, coordinates, scale):
        bpy.context.scene.cursor.location = coordinates * scale
    
    @classmethod
    def get_scale(cls):
        return ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
    
    @classmethod
    def get_coordinates_from_coordinate_output_prop(cls):
        props = bpy.context.scene.BIMGeoreferenceProperties
        coordinates = [float(co) for co in props.coordinate_output.split(",")]
        return coordinates
    
    @classmethod
    def set_ifc_true_north(cls):
        y_angle = -bpy.context.scene.sun_pos_properties.north_offset + radians(90)
        bpy.context.scene.BIMGeoreferenceProperties.true_north_abscissa = str(cos(y_angle))
        bpy.context.scene.BIMGeoreferenceProperties.true_north_ordinate = str(sin(y_angle))

    @classmethod
    def set_blender_true_north(cls):
        bpy.context.scene.sun_pos_properties.north_offset = -radians(
            ifcopenshell.util.geolocation.yaxis2angle(
                float(context.scene.BIMGeoreferenceProperties.true_north_abscissa),
                float(context.scene.BIMGeoreferenceProperties.true_north_ordinate),
            )
        )
    
    @classmethod
    def get_map_conversion(cls):
        ifc = tool.Ifc.get()
        map_conversion = {}
        if ifc.schema == "IFC2X3":
            return
        
        for context in ifc.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if not context.HasCoordinateOperation:
                continue
            
            map_conversion = context.HasCoordinateOperation[0].get_info()
            map_conversion["SourceCRS"] = map_conversion["SourceCRS"].id()
            map_conversion["TargetCRS"] = map_conversion["TargetCRS"].id()
            
            break
        
        return map_conversion
    
    @classmethod
    def get_easting_northing_height_from_xyz(cls, map_conversion):
        props = bpy.context.scene.BIMGeoreferenceProperties
        
        x, y, z = [float(co) for co in props.coordinate_input.split(",")]

        if props.has_blender_offset:
            results = ifcopenshell.util.geolocation.xyz2enh(
                x,
                y,
                z,
                float(props.blender_eastings),
                float(props.blender_northings),
                float(props.blender_orthogonal_height),
                float(props.blender_x_axis_abscissa),
                float(props.blender_x_axis_ordinate),
                1.0,
            )
            x, y, z = results
        
        # TODO: what if the project CRS units and the project units are different?
        
        if map_conversion: #TODO return error when there is the map conversiona but no Xaxis, scale, etc..
            results = ifcopenshell.util.geolocation.xyz2enh(
                x,
                y,
                z,
                map_conversion["Eastings"],
                map_conversion["Northings"],
                map_conversion["OrthogonalHeight"],
                map_conversion.get("XAxisAbscissa", 1.0),
                map_conversion.get("XAxisOrdinate", 0.0),
                map_conversion.get("Scale", 1.0),
            )
        else:
            results = (x, y, z)        
        
        return results
    
    @classmethod
    def get_xyz_from_easting_northig_height(cls, map_conversion):
        props = bpy.context.scene.BIMGeoreferenceProperties
        x, y, z = [float(co) for co in props.coordinate_input.split(",")]

        if map_conversion:
            results = ifcopenshell.util.geolocation.enh2xyz(
                x,
                y,
                z,
                map_conversion["Eastings"],
                map_conversion["Northings"],
                map_conversion["OrthogonalHeight"],
                map_conversion.get("XAxisAbscissa", 1.0),
                map_conversion.get("XAxisOrdinate", 0.0),
                map_conversion.get("Scale", 1.0),
            )
        else:
            results = (x, y, z)

        if props.has_blender_offset:
            results = ifcopenshell.util.geolocation.enh2xyz(
                results[0],
                results[1],
                results[2],
                float(props.blender_eastings),
                float(props.blender_northings),
                float(props.blender_orthogonal_height),
                float(props.blender_x_axis_abscissa),
                float(props.blender_x_axis_ordinate),
                1.0,
            )
            
        return results
    
    @classmethod
    def set_coordinate_output_prop(cls, coordinates):
        props = bpy.context.scene.BIMGeoreferenceProperties
        props.coordinate_output = ",".join([str(r) for r in coordinates])
        
    @classmethod
    def get_x_angle_from_sun_position(cls):
        return -bpy.context.scene.sun_pos_properties.north_offset
    
    @classmethod
    def set_xaxis_vector_from_angle(cls, x_angle):
        bpy.context.scene.BIMGeoreferenceProperties.map_conversion.get("XAxisAbscissa").string_value = str(cos(x_angle))
        bpy.context.scene.BIMGeoreferenceProperties.map_conversion.get("XAxisOrdinate").string_value = str(sin(x_angle))
    
    @classmethod
    def get_angle_from_xaxis(cls):
        return ifcopenshell.util.geolocation.xaxis2angle(
                float(bpy.context.scene.BIMGeoreferenceProperties.map_conversion.get("XAxisAbscissa").string_value),
                float(bpy.context.scene.BIMGeoreferenceProperties.map_conversion.get("XAxisOrdinate").string_value),
            )
    
    @classmethod
    def set_sun_pos_north_offset(cls, angle):
        bpy.context.scene.sun_pos_properties.north_offset = -radians(angle)

