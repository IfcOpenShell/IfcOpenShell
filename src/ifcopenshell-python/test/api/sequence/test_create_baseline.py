# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 IfcOpenShell contributors
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
import ifcopenshell.api.sequence
import test.bootstrap


class TestCreateBaseline(test.bootstrap.IFC4):
    def test_creating_a_baseline_from_a_planned_schedule(self):
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        schedule = ifcopenshell.api.sequence.add_work_schedule(self.file, predefined_type="PLANNED")
        ifcopenshell.api.sequence.create_baseline(self.file, work_schedule=schedule, name="Baseline 1")
        baselines = [ws for ws in self.file.by_type("IfcWorkSchedule") if ws.PredefinedType == "BASELINE"]
        assert len(baselines) == 1
        assert baselines[0].Name == "Baseline 1"

    def test_raising_on_a_non_planned_schedule(self):
        # A schedule that isn't PLANNED (e.g. the ACTUAL default some
        # authoring tools use) has nothing meaningful to baseline.
        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject")
        schedule = ifcopenshell.api.sequence.add_work_schedule(self.file, predefined_type="ACTUAL")
        with pytest.raises(ValueError):
            ifcopenshell.api.sequence.create_baseline(self.file, work_schedule=schedule, name="Baseline 1")
        assert len(self.file.by_type("IfcWorkSchedule")) == 1
