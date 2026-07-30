# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021-2022 Dion Moult <dion@thinkmoult.com>, Yassine Oualid <yassine@sigmadimensions.com>
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

import ifcopenshell.api.root
import ifcopenshell.api.sequence
import test.bootstrap


class TestDuplicateTask(test.bootstrap.IFC4):
    def test_duplicating_a_predecessor_with_a_duration_lag(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        schedule = ifcopenshell.api.sequence.add_work_schedule(self.file, name="Schedule")
        task1 = ifcopenshell.api.sequence.add_task(self.file, work_schedule=schedule, name="Task 1")
        task2 = ifcopenshell.api.sequence.add_task(self.file, work_schedule=schedule, name="Task 2")
        rel = ifcopenshell.api.sequence.assign_sequence(self.file, relating_process=task1, related_process=task2)
        lag = ifcopenshell.api.sequence.assign_lag_time(self.file, rel_sequence=rel, lag_value="P2D")

        originals, duplicates = ifcopenshell.api.sequence.duplicate_task(self.file, task=task1)
        duplicate_task1 = duplicates[0]

        duplicate_rels = list(duplicate_task1.IsPredecessorTo)
        assert len(duplicate_rels) == 1
        duplicate_lag = duplicate_rels[0].TimeLag
        assert duplicate_lag is not None
        assert duplicate_lag.LagValue.is_a("IfcDuration")
        assert duplicate_lag.LagValue.wrappedValue == "P2D"
        # the original relationship and lag are untouched
        assert lag.LagValue.wrappedValue == "P2D"

    def test_duplicating_a_predecessor_with_a_ratio_lag(self):
        # A lag time may also be expressed as a ratio of the predecessor's
        # own duration (e.g. "50% of task 1's duration") instead of a fixed
        # IfcDuration. Duplicating the predecessor must not crash and must
        # preserve the ratio, not silently turn it into a duration lag.
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        schedule = ifcopenshell.api.sequence.add_work_schedule(self.file, name="Schedule")
        task1 = ifcopenshell.api.sequence.add_task(self.file, work_schedule=schedule, name="Task 1")
        task2 = ifcopenshell.api.sequence.add_task(self.file, work_schedule=schedule, name="Task 2")
        rel = ifcopenshell.api.sequence.assign_sequence(self.file, relating_process=task1, related_process=task2)
        lag = ifcopenshell.api.sequence.assign_lag_time(self.file, rel_sequence=rel, lag_value="P1D")
        ifcopenshell.api.sequence.edit_lag_time(self.file, lag_time=lag, attributes={"LagValue": 0.5})

        originals, duplicates = ifcopenshell.api.sequence.duplicate_task(self.file, task=task1)
        duplicate_task1 = duplicates[0]

        duplicate_rels = list(duplicate_task1.IsPredecessorTo)
        assert len(duplicate_rels) == 1
        duplicate_lag = duplicate_rels[0].TimeLag
        assert duplicate_lag is not None
        assert duplicate_lag.LagValue.is_a("IfcRatioMeasure")
        assert duplicate_lag.LagValue.wrappedValue == 0.5
