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
import ifcopenshell.util.element
import pytest

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestAssignZoneToZone(NewFile):
    def test_run(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        parent = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcZone", name="Parent")
        child = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcZone", name="Child")

        bpy.ops.bim.assign_zone_to_zone(zone=parent.id(), zone_to_assign=str(child.id()))

        assert ifcopenshell.util.element.get_grouped_by(parent) == [child]

    def test_a_containing_zone_cannot_be_assigned_back(self):
        ifc = ifcopenshell.file()
        tool.Ifc.set(ifc)
        ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcProject")
        parent = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcZone", name="Parent")
        child = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcZone", name="Child")
        bpy.ops.bim.assign_zone_to_zone(zone=parent.id(), zone_to_assign=str(child.id()))

        with pytest.raises(TypeError):
            bpy.ops.bim.assign_zone_to_zone(zone=child.id(), zone_to_assign=str(parent.id()))

        assert ifcopenshell.util.element.get_grouped_by(child) == []
