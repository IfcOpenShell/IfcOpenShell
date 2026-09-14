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

# This file was generated with the assistance of an AI coding tool.

import ifcopenshell.api.material
import test.bootstrap


class TestRemoveProfile(test.bootstrap.IFC4):
    # IfcMaterialProfileSet does not exist in IFC2X3.
    def test_removing_a_non_last_profile(self):
        profile_set = ifcopenshell.api.material.add_material_set(self.file, set_type="IfcMaterialProfileSet")
        material = ifcopenshell.api.material.add_material(self.file)
        profile_def = self.file.create_entity("IfcArbitraryClosedProfileDef", ProfileType="AREA")
        profile1 = ifcopenshell.api.material.add_profile(
            self.file, profile_set=profile_set, material=material, profile=profile_def
        )
        profile2 = ifcopenshell.api.material.add_profile(
            self.file, profile_set=profile_set, material=material, profile=profile_def
        )
        ifcopenshell.api.material.remove_profile(self.file, profile=profile2)
        assert profile_set.MaterialProfiles == (profile1,)

    def test_removing_the_last_profile_removes_the_whole_set(self):
        profile_set = ifcopenshell.api.material.add_material_set(self.file, set_type="IfcMaterialProfileSet")
        material = ifcopenshell.api.material.add_material(self.file)
        profile_def = self.file.create_entity("IfcArbitraryClosedProfileDef", ProfileType="AREA")
        profile = ifcopenshell.api.material.add_profile(
            self.file, profile_set=profile_set, material=material, profile=profile_def
        )
        ifcopenshell.api.material.remove_profile(self.file, profile=profile)
        assert len(self.file.by_type("IfcMaterialProfileSet")) == 0
        assert len(self.file.by_type("IfcMaterialProfile")) == 0
        assert len(self.file.by_type("IfcMaterial")) == 1
