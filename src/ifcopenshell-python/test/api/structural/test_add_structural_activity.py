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
import ifcopenshell.util.structural
import test.bootstrap


class TestAddStructuralActivity(test.bootstrap.IFC4):
    def add_activity(self, ifc_class="IfcStructuralLinearAction", item_class="IfcStructuralCurveMember", **values):
        item = ifcopenshell.api.root.create_entity(self.file, ifc_class=item_class)
        load = ifcopenshell.api.structural.add_structural_load(self.file, ifc_class="IfcStructuralLoadLinearForce")
        return ifcopenshell.api.structural.add_structural_activity(
            self.file, applied_load=load, structural_member=item, ifc_class=ifc_class, **values
        )

    def test_run(self):
        activity = self.add_activity(predefined_type="CONST", global_or_local="LOCAL_COORDS")
        assert activity.is_a("IfcStructuralLinearAction")
        assert activity.PredefinedType == "CONST"
        assert activity.GlobalOrLocal == "LOCAL_COORDS"
        assert activity.ProjectedOrTrue is None
        assert ifcopenshell.util.structural.get_activity_item(activity).is_a("IfcStructuralCurveMember")

    def test_a_load_per_projected_length(self):
        assert self.add_activity(projected_or_true="PROJECTED_LENGTH").ProjectedOrTrue == "PROJECTED_LENGTH"

    def test_an_area_load_per_projected_area(self):
        activity = self.add_activity(
            ifc_class="IfcStructuralPlanarAction",
            item_class="IfcStructuralSurfaceMember",
            projected_or_true="PROJECTED_LENGTH",
        )
        assert activity.ProjectedOrTrue == "PROJECTED_LENGTH"

    def test_a_local_load_cannot_be_projected(self):
        with pytest.raises(ValueError):
            self.add_activity(global_or_local="LOCAL_COORDS", projected_or_true="PROJECTED_LENGTH")
        assert not self.file.by_type("IfcStructuralActivity")

    def test_a_point_load_cannot_be_projected(self):
        with pytest.raises(ValueError):
            self.add_activity(
                ifc_class="IfcStructuralPointAction",
                item_class="IfcStructuralPointConnection",
                projected_or_true="TRUE_LENGTH",
            )
        assert not self.file.by_type("IfcStructuralActivity")
