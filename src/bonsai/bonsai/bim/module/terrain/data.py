# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Ryan Schultz
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

# This file was generated with the assistance of an AI coding tool.

import bpy

import bonsai.tool as tool


def refresh():
    TerrainData.is_loaded = False


class TerrainData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object) if bpy.context.active_object else None
        settings = tool.Terrain.get_contour_settings(element) if element else None
        datum = tool.Terrain.get_datum(element) if element else None
        cls.data = {
            "datum_source": datum.source if datum else None,
            "datum_height": tool.Unit.blender_format_unit(datum.origin_height) if datum else None,
            "interval": tool.Unit.blender_format_unit(settings[0]) if settings else None,
            "index_interval": settings[1] if settings else None,
            "total_contours": len(tool.Terrain.get_contours(element)) if element else 0,
        }
        cls.is_loaded = True
