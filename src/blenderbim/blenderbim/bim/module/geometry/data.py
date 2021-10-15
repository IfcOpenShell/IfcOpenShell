# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import blenderbim.tool as tool
import ifcopenshell.util.placement


def refresh():
    DerivedPlacementsData.is_loaded = False


class DerivedPlacementsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "is_storey": cls.is_storey(),
            "storey_height": cls.get_storey_height(),
        }
        cls.is_loaded = True

    @classmethod
    def is_storey(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if element:
            return element.is_a("IfcBuildingStorey")

    @classmethod
    def get_storey_height(cls):
        if not cls.is_storey():
            return
        element = tool.Ifc.get_entity(bpy.context.active_object)
        storeys = [
            (s, ifcopenshell.util.placement.get_local_placement(s.ObjectPlacement)[2][3])
            for s in tool.Ifc.get().by_type("IfcBuildingStorey")
        ]
        storeys = sorted(storeys, key=lambda s: s[1])
        for i, storey in enumerate(storeys):
            if storey[0] != element:
                continue
            if i >= len(storeys):
                return "N/A"
            return "{0:.3f}".format(round(storeys[i + 1][1] - storey[1], 3))
