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

class Georeference(blenderbim.core.tool.Georeference):
    
    @classmethod
    def clear_projected_crs(cls):
        bpy.context.scene.BIMGeoreferenceProperties.projected_crs.clear()
    
    @classmethod
    def clear_map_conversion(cls):
        bpy.context.scene.BIMGeoreferenceProperties.map_conversion.clear()
    
    @classmethod
    def set_has_true_north_prop(cls, data):
        bpy.context.scene.BIMGeoreferenceProperties.has_true_north = bool(data)
    
    @classmethod
    def set_true_north_prop(cls, data):
        if data:
            bpy.context.scene.BIMGeoreferenceProperties.true_north_abscissa = str(data[0])
            bpy.context.scene.BIMGeoreferenceProperties.true_north_ordinate = str(data[1])
    
    @classmethod
    def get_true_north_props(cls, props):
        true_north = None
        if props.has_true_north:
            try:
                true_north = [float(props.true_north_abscissa), float(props.true_north_ordinate)]
            except ValueError:
                self.report({"ERROR"}, "True North Abscissa and Ordinate expect a number") #TODO use the correct report method
        return true_north
    
    @classmethod
    def enable_editing(cls):
        bpy.context.scene.BIMGeoreferenceProperties.is_editing = True
    
    @classmethod
    def disable_editing(cls):
        bpy.context.scene.BIMGeoreferenceProperties.is_editing = False
    
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
    
    @classmethod
    def get_cursor_location(cls):
        props = bpy.context.scene.BIMGeoreferenceProperties
        scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        project_coordinates = [o / scale for o in bpy.context.scene.cursor.location]
        props.coordinate_input = ",".join([str(o) for o in project_coordinates])
        
        
    @classmethod
    def set_cursor_location(cls):
        props = bpy.context.scene.BIMGeoreferenceProperties
        scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        bpy.context.scene.cursor.location = [float(co) * scale for co in props.coordinate_output.split(",")]
    
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
    def convert_local_to_global(cls, map_conversion):
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
        
        if map_conversion:
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
        
        props.coordinate_output = ",".join([str(r) for r in results])
        bpy.context.scene.cursor.location = results

    @classmethod
    def convert_global_to_local(cls, map_conversion):
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

        props.coordinate_output = ",".join([str(r) for r in results])

        scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        bpy.context.scene.cursor.location = [o * scale for o in results]

