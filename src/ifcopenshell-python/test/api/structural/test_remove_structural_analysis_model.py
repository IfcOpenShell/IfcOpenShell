# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell.api.root
import ifcopenshell.api.structural
import test.bootstrap


class TestRemoveStructuralAnalysisModel(test.bootstrap.IFC4):
    def test_removing_a_structural_analysis_model(self):
        subject = ifcopenshell.api.structural.add_structural_analysis_model(self.file)
        ifcopenshell.api.structural.remove_structural_analysis_model(
            self.file,
            structural_analysis_model=subject,
        )
        models = self.file.by_type("IfcStructuralAnalysisModel")
        assert len(models) == 0

    def test_removing_its_relationship_to_the_buildings_it_serves(self):
        subject = ifcopenshell.api.structural.add_structural_analysis_model(self.file)
        building = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcBuilding")
        ifcopenshell.api.structural.assign_to_building(self.file, structural_analysis_model=subject, building=building)
        ifcopenshell.api.structural.remove_structural_analysis_model(self.file, structural_analysis_model=subject)
        assert not self.file.by_type("IfcRelServicesBuildings")
        assert self.file.by_type("IfcBuilding") == (building,)


class TestRemoveStructuralAnalysisModelIFC2X3(test.bootstrap.IFC2X3, TestRemoveStructuralAnalysisModel):
    pass
