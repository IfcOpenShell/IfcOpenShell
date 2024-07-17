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


def add_georeferencing(georeference):
    georeference.add_georeferencing()


def enable_editing_georeferencing(georeference):
    georeference.import_projected_crs()
    georeference.import_coordinate_operation()
    georeference.enable_editing()


def remove_georeferencing(ifc):
    ifc.run("georeference.remove_georeferencing")


def disable_editing_georeferencing(georeference):
    georeference.disable_editing()


def edit_georeferencing(ifc, georeference):
    ifc.run(
        "georeference.edit_georeferencing",
        projected_crs=georeference.get_projected_crs_attributes(),
        coordinate_operation=georeference.get_coordinate_operation_attributes(),
    )
    georeference.disable_editing()
    georeference.set_model_origin()


def get_cursor_location(georeference):
    georeference.set_coordinates("local", georeference.get_cursor_location())


def convert_local_to_global(georeference):
    coordinates = georeference.xyz2enh(georeference.get_coordinates("local"))
    georeference.set_coordinates("map", coordinates)
    georeference.set_cursor_location()


def convert_global_to_local(georeference):
    coordinates = georeference.enh2xyz(georeference.get_coordinates("map"))
    georeference.set_coordinates("local", coordinates)
    georeference.set_cursor_location()


def convert_angle_to_coord(georeference, type):
    vector_coordinates = georeference.angle2coords(georeference.get_angle(type), type)
    georeference.set_vector_coordinates(vector_coordinates, type)


def import_plot(georeference, filepath):
    georeference.import_plot(filepath)


def enable_editing_wcs(georeference):
    georeference.import_wcs()
    georeference.enable_editing_wcs()


def disable_editing_wcs(georeference):
    georeference.disable_editing_wcs()


def edit_wcs(ifc, georeference):
    wcs = georeference.export_wcs()
    georeference.set_wcs(wcs)
    georeference.disable_editing_wcs()
    georeference.set_model_origin()


def enable_editing_true_north(georeference):
    georeference.import_true_north()
    georeference.enable_editing_true_north()


def disable_editing_true_north(georeference):
    georeference.disable_editing_true_north()


def edit_true_north(ifc, georeference):
    ifc.run("georeference.edit_true_north", true_north=georeference.get_true_north_attributes())
    georeference.disable_editing_true_north()


def remove_true_north(ifc):
    ifc.run("georeference.edit_true_north", true_north=None)
