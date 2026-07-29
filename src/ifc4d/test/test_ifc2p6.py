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
import re
import tempfile
from pathlib import Path

import ifcopenshell
import ifcopenshell.api.control
import ifcopenshell.api.sequence

from ifc4d.ifc2p6 import Ifc2P6

# P6's Relationship/Lag and Activity/PlannedDuration|RemainingDuration fields
# are plain decimal hours, always calendar (HoursPerDay) scaled - confirmed
# against p62ifc.py's importer (ScheduleIfcGenerator.create_rel_sequences and
# create_task_from_activity in common.py), which both build
# timedelta(days=value / HoursPerDay). Hand-derived at 8h/day:
#   PT12H0M0S -> 12h / 24h-per-day * 8h-per-workday = 4 work-hours
#   P1DT12H0M0S (1 day + 12h) -> 12 work-hours


class TestIfc2P6Lag:
    @staticmethod
    def build_ifc(lag_value: str | None, duration_type: str = "WORKTIME") -> ifcopenshell.file:
        ifc_file = ifcopenshell.file()
        ifc_file.create_entity("IfcProject", GlobalId=ifcopenshell.guid.new(), Name="P")
        schedule = ifcopenshell.api.sequence.add_work_schedule(ifc_file, name="Schedule A")
        calendar = ifcopenshell.api.sequence.add_work_calendar(ifc_file, name="Cal A")
        t1 = ifcopenshell.api.sequence.add_task(ifc_file, work_schedule=schedule, name="T1", identification="1")
        t2 = ifcopenshell.api.sequence.add_task(ifc_file, work_schedule=schedule, name="T2", identification="2")
        ifcopenshell.api.control.assign_control(ifc_file, relating_control=calendar, related_objects=[t1, t2])
        for task in (t1, t2):
            task_time = ifcopenshell.api.sequence.add_task_time(ifc_file, task=task)
            ifcopenshell.api.sequence.edit_task_time(
                ifc_file,
                task_time=task_time,
                attributes={"ScheduleDuration": "P1D", "ScheduleStart": "2024-01-01T08:00:00"},
            )
        rel = ifcopenshell.api.sequence.assign_sequence(ifc_file, relating_process=t1, related_process=t2)
        ifcopenshell.api.sequence.edit_sequence(ifc_file, rel_sequence=rel, attributes={"SequenceType": "FINISH_START"})
        if lag_value is not None:
            ifcopenshell.api.sequence.assign_lag_time(
                ifc_file, rel_sequence=rel, lag_value=lag_value, duration_type=duration_type
            )
        return ifc_file

    @staticmethod
    def export(ifc_file: ifcopenshell.file) -> str:
        converter = Ifc2P6()
        converter.file = ifc_file
        converter.holiday_start_date = datetime.date(2024, 1, 1)
        converter.holiday_finish_date = datetime.date(2024, 1, 1)
        with tempfile.TemporaryDirectory() as tmp_dir:
            converter.xml = str(Path(tmp_dir) / "out.xml")
            converter.execute()
            return Path(converter.xml).read_text()

    def test_sub_day_lag_is_not_truncated(self):
        # Before the fix, only whole days (duration.days) were read, so a
        # pure PT12H0M0S lag (duration.days == 0) exported as Lag "0".
        ifc_file = self.build_ifc("PT12H0M0S", "WORKTIME")
        xml = self.export(ifc_file)
        assert re.findall(r"<Lag>([^<]*)</Lag>", xml) == ["4"]

    def test_mixed_day_and_hour_lag_keeps_the_hour_remainder(self):
        # Before the fix this exported "8" (only the 1 whole day * 8h/day),
        # silently dropping the extra 12 hours.
        ifc_file = self.build_ifc("P1DT12H0M0S", "WORKTIME")
        xml = self.export(ifc_file)
        assert re.findall(r"<Lag>([^<]*)</Lag>", xml) == ["12"]

    def test_negative_lag_is_a_lead(self):
        ifc_file = self.build_ifc("-PT5H", "WORKTIME")
        xml = self.export(ifc_file)
        assert re.findall(r"<Lag>([^<]*)</Lag>", xml) == ["-1.666666667"]

    def test_no_time_lag_exports_zero(self):
        ifc_file = self.build_ifc(None)
        xml = self.export(ifc_file)
        assert re.findall(r"<Lag>([^<]*)</Lag>", xml) == ["0"]


class TestIfc2P6Duration:
    @staticmethod
    def build_ifc(schedule_duration: str) -> ifcopenshell.file:
        ifc_file = ifcopenshell.file()
        ifc_file.create_entity("IfcProject", GlobalId=ifcopenshell.guid.new(), Name="P")
        schedule = ifcopenshell.api.sequence.add_work_schedule(ifc_file, name="Schedule A")
        calendar = ifcopenshell.api.sequence.add_work_calendar(ifc_file, name="Cal A")
        task = ifcopenshell.api.sequence.add_task(ifc_file, work_schedule=schedule, name="T1", identification="1")
        ifcopenshell.api.control.assign_control(ifc_file, relating_control=calendar, related_objects=[task])
        task_time = ifcopenshell.api.sequence.add_task_time(ifc_file, task=task)
        ifcopenshell.api.sequence.edit_task_time(
            ifc_file,
            task_time=task_time,
            attributes={"ScheduleDuration": schedule_duration, "ScheduleStart": "2024-01-01T08:00:00"},
        )
        return ifc_file

    @staticmethod
    def export(ifc_file: ifcopenshell.file) -> str:
        converter = Ifc2P6()
        converter.file = ifc_file
        converter.holiday_start_date = datetime.date(2024, 1, 1)
        converter.holiday_finish_date = datetime.date(2024, 1, 1)
        with tempfile.TemporaryDirectory() as tmp_dir:
            converter.xml = str(Path(tmp_dir) / "out.xml")
            converter.execute()
            return Path(converter.xml).read_text()

    def test_mixed_day_and_hour_duration_keeps_the_hour_remainder(self):
        # Before the fix this exported "8" (only the 1 whole day * 8h/day),
        # silently dropping the extra 4 hours.
        ifc_file = self.build_ifc("P1DT4H0M0S")
        xml = self.export(ifc_file)
        assert re.findall(r"<PlannedDuration>([^<]*)</PlannedDuration>", xml) == ["9.333333333"]
        assert re.findall(r"<RemainingDuration>([^<]*)</RemainingDuration>", xml) == ["9.333333333"]
