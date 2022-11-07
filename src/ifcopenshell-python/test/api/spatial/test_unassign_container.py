# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import numpy
import pytest
import test.bootstrap
import ifcopenshell.api
import ifcopenshell.util.element
import ifcopenshell.util.placement


class TestAssignContainer(test.bootstrap.IFC4):
    def test_unassigning_a_container(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("spatial.assign_container", self.file, product=subelement, relating_structure=element)
        ifcopenshell.api.run("spatial.unassign_container", self.file, product=subelement)
        assert not self.file.by_type("IfcRelContainedInSpatialStructure")

    def test_unassigning_a_container_with_other_elements(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        subelement2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("spatial.assign_container", self.file, product=subelement, relating_structure=element)
        ifcopenshell.api.run("spatial.assign_container", self.file, product=subelement2, relating_structure=element)
        ifcopenshell.api.run("spatial.unassign_container", self.file, product=subelement)
        rel = self.file.by_type("IfcRelContainedInSpatialStructure")[0]
        assert list(rel.RelatedElements) == [subelement2]
