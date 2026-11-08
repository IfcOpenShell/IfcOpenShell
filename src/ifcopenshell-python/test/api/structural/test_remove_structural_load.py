# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Bruno Postle <bruno@postle.net>
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


class TestRemoveStructuralLoad(test.bootstrap.IFC4):
    def test_removing_an_unused_load(self):
        load = ifcopenshell.api.structural.add_structural_load(self.file, ifc_class="IfcStructuralLoadSingleForce")
        ifcopenshell.api.structural.remove_structural_load(self.file, structural_load=load)
        assert not self.file.by_type("IfcStructuralLoad")

    def test_removing_the_activities_that_apply_the_load(self):
        # AppliedLoad is mandatory, so an activity cannot outlive its load
        point = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralPointConnection")
        load = ifcopenshell.api.structural.add_structural_load(self.file, ifc_class="IfcStructuralLoadSingleForce")
        ifcopenshell.api.structural.add_structural_activity(
            self.file, applied_load=load, structural_member=point, ifc_class="IfcStructuralPointAction"
        )
        ifcopenshell.api.structural.remove_structural_load(self.file, structural_load=load)
        assert not self.file.by_type("IfcStructuralLoad")
        assert not self.file.by_type("IfcStructuralActivity")
        assert not self.file.by_type("IfcRelConnectsStructuralActivity")
        assert self.file.by_type("IfcStructuralPointConnection") == (point,)

    def test_keeping_activities_that_apply_another_load(self):
        point = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralPointConnection")
        load = ifcopenshell.api.structural.add_structural_load(self.file, ifc_class="IfcStructuralLoadSingleForce")
        other = ifcopenshell.api.structural.add_structural_load(self.file, ifc_class="IfcStructuralLoadSingleForce")
        activity = ifcopenshell.api.structural.add_structural_activity(
            self.file, applied_load=other, structural_member=point, ifc_class="IfcStructuralPointAction"
        )
        ifcopenshell.api.structural.remove_structural_load(self.file, structural_load=load)
        assert self.file.by_type("IfcStructuralActivity") == (activity,)
        assert activity.AppliedLoad == other


class TestRemoveStructuralLoadIFC2X3(test.bootstrap.IFC2X3, TestRemoveStructuralLoad):
    pass
