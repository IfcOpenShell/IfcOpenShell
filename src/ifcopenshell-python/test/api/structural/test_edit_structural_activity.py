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

import pytest

import ifcopenshell.api.root
import ifcopenshell.api.structural
import test.bootstrap


class TestEditStructuralActivity(test.bootstrap.IFC4):
    def add_activity(self, **values):
        member = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralCurveMember")
        load = ifcopenshell.api.structural.add_structural_load(self.file, ifc_class="IfcStructuralLoadLinearForce")
        return ifcopenshell.api.structural.add_structural_activity(
            self.file, applied_load=load, structural_member=member, ifc_class="IfcStructuralLinearAction", **values
        )

    def test_run(self):
        activity = self.add_activity()
        ifcopenshell.api.structural.edit_structural_activity(
            self.file, activity=activity, attributes={"Name": "Snow", "ProjectedOrTrue": "PROJECTED_LENGTH"}
        )
        assert activity.Name == "Snow"
        assert activity.ProjectedOrTrue == "PROJECTED_LENGTH"

    def test_a_projected_load_turned_local_is_per_true_length(self):
        activity = self.add_activity(projected_or_true="PROJECTED_LENGTH")
        ifcopenshell.api.structural.edit_structural_activity(
            self.file, activity=activity, attributes={"GlobalOrLocal": "LOCAL_COORDS"}
        )
        assert activity.GlobalOrLocal == "LOCAL_COORDS"
        assert activity.ProjectedOrTrue == "TRUE_LENGTH"

    def test_a_local_load_cannot_be_projected(self):
        activity = self.add_activity(global_or_local="LOCAL_COORDS")
        with pytest.raises(ValueError):
            ifcopenshell.api.structural.edit_structural_activity(
                self.file, activity=activity, attributes={"ProjectedOrTrue": "PROJECTED_LENGTH"}
            )
        assert activity.ProjectedOrTrue is None

    def test_projected_and_global_at_once(self):
        activity = self.add_activity(global_or_local="LOCAL_COORDS")
        ifcopenshell.api.structural.edit_structural_activity(
            self.file,
            activity=activity,
            attributes={"GlobalOrLocal": "GLOBAL_COORDS", "ProjectedOrTrue": "PROJECTED_LENGTH"},
        )
        assert activity.GlobalOrLocal == "GLOBAL_COORDS"
        assert activity.ProjectedOrTrue == "PROJECTED_LENGTH"

    def test_a_point_load_turned_local(self):
        point = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcStructuralPointConnection")
        load = ifcopenshell.api.structural.add_structural_load(self.file, ifc_class="IfcStructuralLoadSingleForce")
        activity = ifcopenshell.api.structural.add_structural_activity(
            self.file, applied_load=load, structural_member=point, ifc_class="IfcStructuralPointAction"
        )
        ifcopenshell.api.structural.edit_structural_activity(
            self.file, activity=activity, attributes={"GlobalOrLocal": "LOCAL_COORDS"}
        )
        assert activity.GlobalOrLocal == "LOCAL_COORDS"
