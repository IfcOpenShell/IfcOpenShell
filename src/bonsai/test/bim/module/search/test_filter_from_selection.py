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
import ifcopenshell.api.root
import ifcopenshell.api.spatial

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestFilterFromSelection(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        storey = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcBuildingStorey", name="G1")
        for ifc_class in ("IfcWall", "IfcSlab"):
            element = ifcopenshell.api.root.create_entity(ifc, ifc_class=ifc_class)
            ifcopenshell.api.spatial.assign_container(ifc, products=[element], relating_structure=storey)
            obj = bpy.data.objects.new(ifc_class, None)
            bpy.context.scene.collection.objects.link(obj)
            tool.Ifc.link(element, obj)
            obj.select_set(True)

        bpy.ops.bim.filter_from_selection()

        query = tool.Search.export_filter_query(tool.Search.get_search_props().filter_groups)
        assert query == 'IfcSlab, location="G1" + IfcWall, location="G1"'
