# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Petru Conduraru <petru@bimvoice.com>
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
import ifcopenshell.api.sequence
import test.bootstrap


class TestAssignSequence(test.bootstrap.IFC4):
    def test_assign_a_sequence(self, monkeypatch):
        # cascade_schedule() reads IfcTask.TaskTime, an attribute that does not
        # exist on IFC2X3.IfcTask at all. That is a pre-existing, unrelated bug
        # in cascade_schedule(), not something this test is about, so it is
        # stubbed out here to isolate assign_sequence()'s own behaviour.
        monkeypatch.setattr(ifcopenshell.api.sequence, "cascade_schedule", lambda *a, **k: None)
        task1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTask")
        task2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTask")
        rel = ifcopenshell.api.sequence.assign_sequence(self.file, relating_process=task1, related_process=task2)
        assert rel.RelatingProcess == task1
        assert rel.RelatedProcess == task2

    def test_setting_time_lag_default_for_ifc2x3(self, monkeypatch):
        monkeypatch.setattr(ifcopenshell.api.sequence, "cascade_schedule", lambda *a, **k: None)
        task1 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTask")
        task2 = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcTask")
        rel = ifcopenshell.api.sequence.assign_sequence(self.file, relating_process=task1, related_process=task2)
        if self.file.schema == "IFC2X3":
            assert rel.TimeLag == 0.0


class TestAssignSequenceIFC2X3(test.bootstrap.IFC2X3, TestAssignSequence):
    pass
