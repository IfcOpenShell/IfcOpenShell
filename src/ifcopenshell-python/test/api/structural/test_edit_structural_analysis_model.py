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

import test.bootstrap
import ifcopenshell.api.structural


class TestEditStructuralAnalysisModel(test.bootstrap.IFC4):
    def test_editing_a_structural_analysis_model(self):
        subject = ifcopenshell.api.structural.add_structural_analysis_model(self.file)
        ifcopenshell.api.structural.edit_structural_analysis_model(
            self.file,
            structural_analysis_model=subject,
            attributes={"Name": "My edited model", "Description": "Description of my model"},
        )
        models = self.file.by_type("IfcStructuralAnalysisModel")
        assert subject == models[0]
        assert subject.is_a("IfcStructuralAnalysisModel")


class TestEditStructuralAnalysisModelIFC2X3(test.bootstrap.IFC2X3, TestEditStructuralAnalysisModel):
    pass
