# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import bonsai.tool as tool


def add_georeferencing(georeference: tool.Georeference) -> None:
    georeference.add_georeferencing()


def enable_editing_georeferencing(georeference: tool.Georeference) -> None:
    georeference.import_projected_crs()
    georeference.import_coordinate_operation()
    georeference.enable_editing()


def remove_georeferencing(ifc: tool.Ifc) -> None:
    ifc.run("georeference.remove_georeferencing")


def disable_editing_georeferencing(georeference: tool.Georeference) -> None:
    georeference.disable_editing()


def edit_georeferencing(ifc: tool.Ifc, georeference: tool.Georeference) -> None:
    ifc.run(
        "georeference.edit_georeferencing",
        projected_crs=georeference.export_projected_crs(),
        coordinate_operation=georeference.export_coordinate_operation(),
    )
    georeference.disable_editing()
    georeference.set_model_origin()


def get_cursor_location(georeference: tool.Georeference) -> None:
    location = georeference.get_cursor_location()
    if georeference.has_blender_offset():
        georeference.set_coordinates("blender", location)
    else:
        georeference.set_coordinates("local", location)


def import_plot(georeference: tool.Georeference, filepath: str) -> None:
    georeference.import_plot(filepath)


def enable_editing_wcs(georeference: tool.Georeference) -> None:
    georeference.import_wcs()
    georeference.enable_editing_wcs()


def disable_editing_wcs(georeference: tool.Georeference) -> None:
    georeference.disable_editing_wcs()


def edit_wcs(georeference: tool.Georeference) -> None:
    wcs = georeference.export_wcs()
    georeference.set_wcs(wcs)
    georeference.disable_editing_wcs()
    georeference.set_model_origin()


def enable_editing_true_north(georeference: tool.Georeference) -> None:
    georeference.import_true_north()
    georeference.enable_editing_true_north()


def disable_editing_true_north(georeference: tool.Georeference) -> None:
    georeference.disable_editing_true_north()


def edit_true_north(ifc: tool.Ifc, georeference: tool.Georeference) -> None:
    ifc.run("georeference.edit_true_north", true_north=georeference.get_true_north_attributes())
    georeference.disable_editing_true_north()


def remove_true_north(ifc: tool.Ifc) -> None:
    ifc.run("georeference.edit_true_north", true_north=None)
