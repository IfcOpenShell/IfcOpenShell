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
#
# This file was generated with the assistance of an AI coding tool.

import datetime

import ifcopenshell
import ifcopenshell.api.root
import ifcopenshell.api.unit

from ifc4d.common import ScheduleIfcGenerator

# ScheduleIfcGenerator.create_task_from_activity() is shared by P62Ifc (P6 XML),
# P6XER2Ifc (P6 XER) and PP2Ifc (Asta Powerproject). A zero-duration activity is
# a normal, meaningful value (e.g. a milestone: PlannedDuration is explicitly 0
# hours and StartDate == FinishDate). It must not silently turn into a full day.


def build_settings(planned_duration):
    return {
        "work_plan": None,
        "project": {"Name": "Test Project"},
        "calendars": {
            "C1": {
                "Name": "Cal1",
                "Type": "Global",
                "HoursPerDay": "8",
                "StandardWorkWeek": [],
                "HolidayOrExceptions": {},
            }
        },
        "wbs": {},
        "root_activities": ["A1"],
        "activities": {
            "A1": {
                "Name": "Activity",
                "Identification": "1",
                "StartDate": datetime.datetime(2024, 1, 1),
                "FinishDate": datetime.datetime(2024, 1, 1),
                "PlannedDuration": planned_duration,
                "Status": "NotStarted",
                "CalendarObjectId": "C1",
                "ifc": None,
            }
        },
        "relationships": {},
        "resources": {},
    }


def convert(planned_duration) -> ifcopenshell.entity_instance:
    ifc_file = ifcopenshell.file(schema="IFC4")
    ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject", name="Test")
    ifcopenshell.api.unit.assign_unit(ifc_file)
    work_plan = ifc_file.create_entity("IfcWorkPlan")
    generator = ScheduleIfcGenerator(ifc_file, None, build_settings(planned_duration))
    generator.work_plan = work_plan
    generator.create_ifc()
    return generator.activities["A1"]["ifc"]


class TestCreateTaskFromActivityZeroDuration:
    def test_string_zero_duration_is_p0d_not_p1d(self):
        # P62Ifc parses PlannedDuration as a string straight from XML .text.
        task = convert("0")
        assert task.TaskTime.ScheduleDuration == "P0D"
        assert task.TaskTime.ScheduleFinish == task.TaskTime.ScheduleStart

    def test_float_zero_duration_is_p0d_not_p1d(self):
        # P6XER2Ifc (target_drtn_hr_cnt) and PP2Ifc (activity_duration for a
        # MILESTONE bar) both pass PlannedDuration as a Python float.
        task = convert(0.0)
        assert task.TaskTime.ScheduleDuration == "P0D"
        assert task.TaskTime.ScheduleFinish == task.TaskTime.ScheduleStart

    def test_nonzero_duration_is_unaffected(self):
        # 16 hours / 8 hours-per-day = 2 days.
        task = convert("16")
        assert task.TaskTime.ScheduleDuration == "P2D"
