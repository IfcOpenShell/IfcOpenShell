# This file was generated with the assistance of an AI coding tool.
# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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
import ifcopenshell.api.layer
import ifcopenshell.api.root

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestEnableEditingLayer(NewFile):
    def test_a_stale_layer_id_is_ignored(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        layer = ifcopenshell.api.layer.add_layer(ifc, name="Stale")
        layer_id = layer.id()
        ifcopenshell.api.layer.remove_layer(ifc, layer=layer)

        result = bpy.ops.bim.enable_editing_layer(layer=layer_id)

        assert result == {"CANCELLED"}
