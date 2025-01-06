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
    def total_layers(cls):
        return len(tool.Ifc.get().by_type("IfcPresentationLayerAssignment"))

    @classmethod
    def active_layers(cls):
        if not bpy.context.active_object:
            return []
        data = bpy.context.active_object.data
        if not data:
            return []
        if not isinstance(data, bpy.types.Mesh) or not data.BIMMeshProperties.ifc_definition_id:
            return []
        results = dict()
        shape = tool.Ifc.get().by_id(data.BIMMeshProperties.ifc_definition_id)
        for inverse in shape.LayerAssignments:
            results[inverse.id()] = inverse.Name or "Unnamed"
        return results
