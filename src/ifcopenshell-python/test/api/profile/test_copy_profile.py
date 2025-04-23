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

import test.bootstrap
import ifcopenshell.api.profile
import ifcopenshell.api.pset
import ifcopenshell.util.element


class TestCopyProfileIFC2X3(test.bootstrap.IFC2X3):
    def test_copy_profile(self):
        profile = ifcopenshell.api.profile.add_parameterized_profile(self.file, "IfcRectangleProfileDef")
        new_profile = ifcopenshell.api.profile.copy_profile(self.file, profile=profile)
        assert new_profile.is_a("IfcRectangleProfileDef")
        assert profile != new_profile
        assert len(self.file.by_type("IfcRectangleProfileDef")) == 2

    def test_copy_profile_with_pset(self):
        profile = ifcopenshell.api.profile.add_parameterized_profile(self.file, "IfcRectangleProfileDef")
        pset = ifcopenshell.api.pset.add_pset(self.file, product=profile, name="ProfilePset")
        new_profile = ifcopenshell.api.profile.copy_profile(self.file, profile=profile)

        assert len(self.file.by_type("IfcRectangleProfileDef")) == 2
        assert len(psets := self.file.by_type("IfcProfileProperties")) == 2
        assert ifcopenshell.util.element.get_elements_by_pset(pset) == {profile}
        assert ifcopenshell.util.element.get_elements_by_pset(psets[1]) == {new_profile}


class TestCopyProfileIFC4(test.bootstrap.IFC4, TestCopyProfileIFC2X3):
    pass
