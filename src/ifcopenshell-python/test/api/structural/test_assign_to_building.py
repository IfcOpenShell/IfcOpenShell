# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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
# This file was generated with the assistance of an AI coding tool.

import ifcopenshell.api.root
import ifcopenshell.api.structural
import test.bootstrap


class TestAssignToBuilding(test.bootstrap.IFC4):
    def test_creating_a_new_relationship(self):
        model = ifcopenshell.api.structural.add_structural_analysis_model(self.file)
        building = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        rel = ifcopenshell.api.structural.assign_to_building(
            self.file, structural_analysis_model=model, building=building
        )
        assert rel.is_a("IfcRelServicesBuildings")
        assert rel.RelatingSystem == model
        assert building in rel.RelatedBuildings

    def test_adding_a_second_building_to_an_existing_relationship(self):
        model = ifcopenshell.api.structural.add_structural_analysis_model(self.file)
        building1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        building2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        rel1 = ifcopenshell.api.structural.assign_to_building(
            self.file, structural_analysis_model=model, building=building1
        )
        rel2 = ifcopenshell.api.structural.assign_to_building(
            self.file, structural_analysis_model=model, building=building2
        )
        assert rel1 == rel2
        assert len(self.file.by_type("IfcRelServicesBuildings")) == 1
        assert building1 in rel1.RelatedBuildings
        assert building2 in rel1.RelatedBuildings

    def test_does_not_duplicate_an_existing_assignment(self):
        model = ifcopenshell.api.structural.add_structural_analysis_model(self.file)
        building = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        ifcopenshell.api.structural.assign_to_building(self.file, structural_analysis_model=model, building=building)
        ifcopenshell.api.structural.assign_to_building(self.file, structural_analysis_model=model, building=building)
        assert len(self.file.by_type("IfcRelServicesBuildings")) == 1
        rels = self.file.by_type("IfcRelServicesBuildings")
        assert len(rels[0].RelatedBuildings) == 1


class TestAssignToBuildingIFC2X3(test.bootstrap.IFC2X3, TestAssignToBuilding):
    pass
