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

def add_georeferencing(ifc):
    ifc.run("georeference.add_georeferencing")

def enable_editing_georeferencing(georeference):
    georeference.clear_projected_crs()
    georeference.import_projected_crs()
    georeference.clear_map_conversion()
    georeference.import_map_conversion()
    georeference.set_has_true_north_prop()
    georeference.set_true_north_props()
    georeference.enable_editing()
    
def remove_georeferencing(ifc):
    ifc.run("georeference.remove_georeferencing")

def disable_editing_georeferencing(georeference):
    georeference.disable_editing()
    
def edit_georeferencing(ifc, georeference):
    projected_crs = georeference.get_projected_crs_attributes()
    map_conversion = georeference.get_map_conversion_attributes()
    true_north = georeference.get_true_north_attributes()
    georeference.edit_georeferencing(projected_crs, map_conversion, true_north)
    georeference.disable_editing()
    
def set_ifc_grid_north(georeference):
    x_angle = georeference.get_x_angle_from_sun_position()
    georeference.set_xaxis_vector_from_angle(x_angle)
    
def set_blender_grid_north(georeference):
    angle = georeference.get_angle_from_xaxis()
    georeference.set_sun_pos_north_offset(angle)

def get_cursor_location(georeference):
    georeference.get_cursor_location()
    
def set_cursor_location(georeference):
    scale = georeference.get_scale()
    coordinates = georeference.get_coordinates_from_coordinate_output_prop()
    georeference.set_cursor_location(coordinates, scale)

def set_ifc_true_north(georeference):
    georeference.set_ifc_true_north()

def set_blender_true_north(georeference):
    georeference.set_blender_true_north()

def convert_local_to_global(georeference):
    map_conversion = georeference.get_map_conversion()
    coordinates = georeference.get_easting_northing_height_from_xyz(map_conversion)
    georeference.set_coordinate_output_prop(coordinates)
    georeference.set_cursor_location(coordinates, scale = 1)
    
def convert_global_to_local(georeference):
    map_conversion = georeference.get_map_conversion()
    coordinates = georeference.get_xyz_from_easting_northig_height(map_conversion)
    georeference.set_coordinate_output_prop(coordinates)
    scale = georeference.get_scale()
    georeference.set_cursor_location(coordinates, scale)

