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


class TestRemoveStructuralLoadGroup(test.bootstrap.IFC4):
    def test_removing_a_load_group(self):
        group = ifcopenshell.api.structural.add_structural_load_group(self.file)
        ifcopenshell.api.structural.remove_structural_load_group(self.file, load_group=group)
        assert not self.file.by_type("IfcStructuralLoadGroup")

    def test_removing_the_last_load_group_of_a_model_unsets_loaded_by(self):
        model = ifcopenshell.api.structural.add_structural_analysis_model(self.file)
        group = ifcopenshell.api.structural.add_structural_load_group(self.file)
        ifcopenshell.api.structural.assign_structural_load_group(
            self.file, load_groups=[group], structural_analysis_model=model
        )
        ifcopenshell.api.structural.remove_structural_load_group(self.file, load_group=group)
        assert model.LoadedBy is None


class TestRemoveStructuralLoadGroupIFC2X3(test.bootstrap.IFC2X3, TestRemoveStructuralLoadGroup):
    pass
