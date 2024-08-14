# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import bpy
import bonsai.tool as tool
import ifcopenshell.util.geolocation
from mathutils import Vector


def refresh():
    SolarData.is_loaded = False


class SolarData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {
            "sun_position": cls.sun_position(),
            "sites": cls.sites(),
            "true_north": cls.true_north(),
        }

    @classmethod
    def sun_position(cls):
        return tool.Blender.get_sun_position_addon()

    @classmethod
    def sites(cls):
        results = []
        for site in tool.Ifc.get().by_type("IfcSite"):
            if site.RefLatitude and site.RefLongitude:
                name = site.Name or "Unnamed"
                description = site.LongName or site.Description or ""
                lat = round(ifcopenshell.util.geolocation.dms2dd(*site.RefLatitude), 3)
                long = round(ifcopenshell.util.geolocation.dms2dd(*site.RefLongitude), 3)
                results.append((str(site.id()), f"{name} - {lat},{long}", description))
        return results

    @classmethod
    def true_north(cls):
        for context in tool.Ifc.get().by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            if not context.TrueNorth:
                continue
            value = context.TrueNorth.DirectionRatios
            return round(ifcopenshell.util.geolocation.yaxis2angle(*value[:2]), 4)
