# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell
import bonsai.tool as tool


def refresh():
    LayersData.is_loaded = False


class LayersData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"total_layers": cls.total_layers(), "active_layers": cls.active_layers()}
        cls.is_loaded = True

    @classmethod
    def total_layers(cls) -> int:
        return len(tool.Ifc.get().by_type("IfcPresentationLayerAssignment"))

    @classmethod
    def active_layers(cls) -> dict[int, str]:
        results = {}
        if not (obj := bpy.context.active_object) or not (shape := tool.Geometry.get_active_representation(obj)):
            return results

        attr_name = None
        if shape.is_a("IfcShapeModel"):
            attr_name = "LayerAssignments"
        elif shape.is_a("IfcRepresentationItem"):
            attr_name = "LayerAssignment"
        if attr_name is None:
            return results
        return {layer.id(): layer.Name for layer in getattr(shape, attr_name)}
