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
import ifcopenshell

from blenderbim.bim.module.georeference.data import GeoreferenceData

def add_georeferencing(ifc):
    ifc.run("georeference.add_georeferencing")

def enable_editing_georeferencing(georeference): #TODO simplify this function
    georeference.clear_projected_crs()
    
    blenderbim.bim.helper.import_attributes(
        "IfcProjectedCRS",
        bpy.context.scene.BIMGeoreferenceProperties.projected_crs,
        GeoreferenceData.data["projected_crs"],
        georeference.import_projected_crs_attributes,
    )
    
    georeference.clear_map_conversion()
    
    blenderbim.bim.helper.import_attributes(
            "IfcMapConversion",
            bpy.context.scene.BIMGeoreferenceProperties.map_conversion,
            GeoreferenceData.data["map_conversion"],
            georeference.import_map_conversion_attributes,
        )
    
    bpy.context.scene.BIMGeoreferenceProperties.has_true_north = bool(GeoreferenceData.data["true_north"])
    
    if GeoreferenceData.data["true_north"]:
        bpy.context.scene.BIMGeoreferenceProperties.true_north_abscissa = str(GeoreferenceData.data["true_north"][0])
        bpy.context.scene.BIMGeoreferenceProperties.true_north_ordinate = str(GeoreferenceData.data["true_north"][1])
    
    bpy.context.scene.BIMGeoreferenceProperties.is_editing = True
    
def remove_georeferencing(ifc):
    ifc.run("georeference.remove_georeferencing")
    
def edit_georeferencing(ifc, georeference):
    props = bpy.context.scene.BIMGeoreferenceProperties
    ifc_file = georeference.get_file()

    projected_crs = blenderbim.bim.helper.export_attributes(props.projected_crs, georeference.export_crs_attributes)
    map_conversion = blenderbim.bim.helper.export_attributes(props.map_conversion, georeference.export_map_attributes)

    true_north = None
#    if props.has_true_north:
#        try:
#            true_north = [float(props.true_north_abscissa), float(props.true_north_ordinate)]
#        except ValueError:
#            self.report({"ERROR"}, "True North Abscissa and Ordinate expect a number")

    ifcopenshell.api.run( #TODO use ifc.run
        "georeference.edit_georeferencing",
        ifc_file,
        **{
            "map_conversion": map_conversion,
            "projected_crs": projected_crs,
            "true_north": true_north,
        }
    )

    bpy.ops.bim.disable_editing_georeferencing()

def disable_editing_georeferencing(georeference):
    georeference.set_false_is_editing()
    
def set_ifc_grid_north(georeference):
    georeference.set_ifc_grid_north()
    
def set_blender_grid_north(georeference):
    georeference.set_blender_grid_north()


