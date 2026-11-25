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


class TestUnassignFromBuilding(test.bootstrap.IFC4):
    def test_removing_the_relationship_with_its_last_building(self):
        model = ifcopenshell.api.structural.add_structural_analysis_model(self.file)
        building = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        ifcopenshell.api.structural.assign_to_building(self.file, structural_analysis_model=model, building=building)
        ifcopenshell.api.structural.unassign_from_building(
            self.file, structural_analysis_model=model, building=building
        )
        assert not self.file.by_type("IfcRelServicesBuildings")
        assert not model.ServicesBuildings

    def test_keeping_the_relationship_for_other_buildings(self):
        model = ifcopenshell.api.structural.add_structural_analysis_model(self.file)
        building1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        building2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        ifcopenshell.api.structural.assign_to_building(self.file, structural_analysis_model=model, building=building1)
        rel = ifcopenshell.api.structural.assign_to_building(
            self.file, structural_analysis_model=model, building=building2
        )
        ifcopenshell.api.structural.unassign_from_building(
            self.file, structural_analysis_model=model, building=building1
        )
        assert rel.RelatedBuildings == (building2,)

    def test_doing_nothing_for_a_building_not_served(self):
        model = ifcopenshell.api.structural.add_structural_analysis_model(self.file)
        building1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        building2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        rel = ifcopenshell.api.structural.assign_to_building(
            self.file, structural_analysis_model=model, building=building1
        )
        ifcopenshell.api.structural.unassign_from_building(
            self.file, structural_analysis_model=model, building=building2
        )
        assert rel.RelatedBuildings == (building1,)


class TestUnassignFromBuildingIFC2X3(test.bootstrap.IFC2X3, TestUnassignFromBuilding):
    pass
