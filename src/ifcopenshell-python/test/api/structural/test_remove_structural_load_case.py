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

import ifcopenshell.api.structural
import test.bootstrap


class TestRemoveStructuralLoadCase(test.bootstrap.IFC4):
    # IfcStructuralLoadCase does not exist in IFC2X3, so add_structural_load_case
    # (and therefore this test) is IFC4+ only.
    def test_removing_a_structural_load_case_without_owner_history(self):
        # OwnerHistory is not set by add_structural_load_case, so it is None
        # by default. Removal must not crash on that common case.
        load_case = ifcopenshell.api.structural.add_structural_load_case(self.file, name="LC1")
        assert load_case.OwnerHistory is None
        ifcopenshell.api.structural.remove_structural_load_case(self.file, load_case=load_case)
        assert len(self.file.by_type("IfcStructuralLoadCase")) == 0
