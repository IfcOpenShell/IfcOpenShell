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
import blenderbim.bim.helper

from blenderbim.bim.module.georeference.data import GeoreferenceData

from math import radians, degrees, atan, tan, cos, sin

def add_georeferencing(ifc):
    ifc.run("georeference.add_georeferencing")

def enable_editing_georeferencing(georeference):
    props = bpy.context.scene.BIMGeoreferenceProperties
    
    georeference.clear_projected_crs()
    
    blenderbim.bim.helper.import_attributes(
        "IfcProjectedCRS",
        props.projected_crs,
        GeoreferenceData.data["projected_crs"],
        georeference.import_projected_crs_attributes,
    )
       
    georeference.clear_map_conversion()
        
    blenderbim.bim.helper.import_attributes(
            "IfcMapConversion",
            props.map_conversion,
            GeoreferenceData.data["map_conversion"],
            georeference.import_map_conversion_attributes,
        )
    
    georeference.set_has_true_north_prop(GeoreferenceData.data["true_north"])
    georeference.set_true_north_prop(GeoreferenceData.data["true_north"])
    georeference.enable_editing()
    
def remove_georeferencing(ifc):
    ifc.run("georeference.remove_georeferencing")
    
def edit_georeferencing(ifc, georeference):
    props = bpy.context.scene.BIMGeoreferenceProperties

    projected_crs = blenderbim.bim.helper.export_attributes(props.projected_crs, georeference.export_crs_attributes)
    map_conversion = blenderbim.bim.helper.export_attributes(props.map_conversion, georeference.export_map_attributes)
    
    true_north = georeference.get_true_north_props(props)
    
    ifc.run(
        "georeference.edit_georeferencing",
        **{
            "map_conversion": map_conversion,
            "projected_crs": projected_crs,
            "true_north": true_north,
        }
    )
    
    georeference.disable_editing()
    
def set_ifc_grid_north(georeference):
    georeference.set_ifc_grid_north()
    
def set_blender_grid_north(georeference):
    georeference.set_blender_grid_north()

def get_cursor_location(georeference):
    georeference.get_cursor_location()
    
def set_cursor_location(georeference):
    georeference.set_cursor_location()

def set_ifc_true_north(georeference):
    georeference.set_ifc_true_north()

def set_blender_true_north(georeference):
    georeference.set_blender_true_north()

def convert_local_to_global(georeference):
    georeference.convert_local_to_global(GeoreferenceData.data["map_conversion"])
    
def convert_global_to_local(georeference):
    georeference.convert_global_to_local(GeoreferenceData.data["map_conversion"])

