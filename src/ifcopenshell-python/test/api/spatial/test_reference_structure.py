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

import pytest
import test.bootstrap
import ifcopenshell.api
import ifcopenshell.util.element


class TestReferenceStructure(test.bootstrap.IFC4):
    def test_referencing_a_structure(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        rel = ifcopenshell.api.run(
            "spatial.reference_structure", self.file, product=subelement, relating_structure=element
        )
        assert ifcopenshell.util.element.get_referenced_structures(subelement) == [element]
        assert rel.is_a("IfcRelReferencedInSpatialStructure")

    def test_doing_nothing_if_the_structure_is_already_referenced(self):
        element = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        subelement = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("spatial.reference_structure", self.file, product=subelement, relating_structure=element)
        total_elements = len([e for e in self.file])
        ifcopenshell.api.run("spatial.reference_structure", self.file, product=subelement, relating_structure=element)
        assert len([e for e in self.file]) == total_elements

    def test_that_old_relationships_are_updated_if_they_still_contain_elements(self):
        element1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcBuilding")
        subelement1 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        subelement2 = ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcWall")
        ifcopenshell.api.run("spatial.reference_structure", self.file, product=subelement1, relating_structure=element1)
        ifcopenshell.api.run("spatial.reference_structure", self.file, product=subelement2, relating_structure=element1)
        rel = subelement1.ReferencedInStructures[0]
        assert len(rel.RelatedElements) == 2
