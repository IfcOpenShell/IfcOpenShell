# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Ryan Schultz
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

import ifcopenshell.api.structural
import test.bootstrap


class TestUnassignStructuralLoadGroup(test.bootstrap.IFC4):
    def test_unassigning_keeps_the_other_load_groups(self):
        model = ifcopenshell.api.structural.add_structural_analysis_model(self.file)
        group1 = ifcopenshell.api.structural.add_structural_load_group(self.file)
        group2 = ifcopenshell.api.structural.add_structural_load_group(self.file)
        ifcopenshell.api.structural.assign_structural_load_group(
            self.file, load_groups=[group1, group2], structural_analysis_model=model
        )
        ifcopenshell.api.structural.unassign_structural_load_group(
            self.file, load_groups=[group1], structural_analysis_model=model
        )
        assert model.LoadedBy == (group2,)

    def test_unassigning_the_last_load_group_unsets_loaded_by(self):
        model = ifcopenshell.api.structural.add_structural_analysis_model(self.file)
        group = ifcopenshell.api.structural.add_structural_load_group(self.file)
        ifcopenshell.api.structural.assign_structural_load_group(
            self.file, load_groups=[group], structural_analysis_model=model
        )
        ifcopenshell.api.structural.unassign_structural_load_group(
            self.file, load_groups=[group], structural_analysis_model=model
        )
        assert model.LoadedBy is None


class TestUnassignStructuralLoadGroupIFC2X3(test.bootstrap.IFC2X3, TestUnassignStructuralLoadGroup):
    pass
