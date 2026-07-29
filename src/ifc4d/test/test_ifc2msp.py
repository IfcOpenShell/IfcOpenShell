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

import re
import tempfile
from pathlib import Path

import ifcopenshell
import ifcopenshell.api.sequence

from ifc4d.ifc2msp import Ifc2Msp

# LinkLag/LagFormat unit convention verified against msp2ifc.py's importer
# (see #9043, which fixed the same LinkLag field on import): the value is
# tenths of a minute, and LagFormat 7 ("Days") means the number should be
# read back through the calendar's hours_per_day, while LagFormat 8
# ("Elapsed Days") means it is real clock hours. Round-tripped by hand:
#   PT12H0M0S at 8h/day -> 4 work-hours -> 4 * 60 * 10 = 2400 tenths
#   P1DT12H0M0S (1 day + 12h) at 8h/day -> 12 work-hours -> 7200 tenths
#   P2D as ELAPSEDTIME -> 48 real hours -> 48 * 60 * 10 = 28800 tenths
#   -PT5H (a lead) at 8h/day -> -1.6667 work-hours -> -1000 tenths


class TestIfc2MspLag:
    @staticmethod
    def build_ifc(lag_value: str | None, duration_type: str = "WORKTIME") -> ifcopenshell.file:
        ifc_file = ifcopenshell.file()
        ifc_file.create_entity("IfcProject", GlobalId=ifcopenshell.guid.new(), Name="P")
        schedule = ifcopenshell.api.sequence.add_work_schedule(ifc_file, name="Schedule A")
        t1 = ifcopenshell.api.sequence.add_task(ifc_file, work_schedule=schedule, name="T1", identification="1")
        t2 = ifcopenshell.api.sequence.add_task(ifc_file, work_schedule=schedule, name="T2", identification="2")
        rel = ifcopenshell.api.sequence.assign_sequence(ifc_file, relating_process=t1, related_process=t2)
        ifcopenshell.api.sequence.edit_sequence(ifc_file, rel_sequence=rel, attributes={"SequenceType": "FINISH_START"})
        if lag_value is not None:
            ifcopenshell.api.sequence.assign_lag_time(
                ifc_file, rel_sequence=rel, lag_value=lag_value, duration_type=duration_type
            )
        return ifc_file

    @staticmethod
    def export(ifc_file: ifcopenshell.file) -> str:
        converter = Ifc2Msp()
        converter.file = ifc_file
        converter.work_schedule = ifc_file.by_type("IfcWorkSchedule")[0]
        with tempfile.TemporaryDirectory() as tmp_dir:
            converter.xml = str(Path(tmp_dir) / "out.xml")
            converter.execute()
            return Path(converter.xml).read_text()

    @staticmethod
    def get_fields(xml_text: str, tag: str) -> list[str]:
        return re.findall(rf"<{tag}>([^<]*)</{tag}>", xml_text)

    def test_sub_day_worktime_lag_is_not_truncated(self):
        # Before the fix, only whole days (duration.days) were read, so a
        # pure PT12H0M0S lag (duration.days == 0) exported as LinkLag "0".
        ifc_file = self.build_ifc("PT12H0M0S", "WORKTIME")
        xml = self.export(ifc_file)
        assert self.get_fields(xml, "LinkLag") == ["2400"]
        assert self.get_fields(xml, "LagFormat") == ["7"]

    def test_mixed_day_and_hour_worktime_lag_keeps_the_hour_remainder(self):
        # Before the fix this exported "4800" (only the 1 whole day),
        # silently dropping the extra 12 hours.
        ifc_file = self.build_ifc("P1DT12H0M0S", "WORKTIME")
        xml = self.export(ifc_file)
        assert self.get_fields(xml, "LinkLag") == ["7200"]

    def test_elapsedtime_lag_uses_24_hour_days_not_the_calendar(self):
        ifc_file = self.build_ifc("P2D", "ELAPSEDTIME")
        xml = self.export(ifc_file)
        assert self.get_fields(xml, "LinkLag") == ["28800"]
        assert self.get_fields(xml, "LagFormat") == ["8"]

    def test_negative_lag_is_a_lead(self):
        ifc_file = self.build_ifc("-PT5H", "WORKTIME")
        xml = self.export(ifc_file)
        assert self.get_fields(xml, "LinkLag") == ["-1000"]

    def test_zero_lag_still_exports_zero(self):
        ifc_file = self.build_ifc("PT0H0M0S", "WORKTIME")
        xml = self.export(ifc_file)
        assert self.get_fields(xml, "LinkLag") == ["0"]

    def test_no_time_lag_exports_zero(self):
        ifc_file = self.build_ifc(None)
        xml = self.export(ifc_file)
        assert self.get_fields(xml, "LinkLag") == ["0"]


class TestIfc2MspTaskDuration:
    @staticmethod
    def build_ifc(schedule_duration: str) -> ifcopenshell.file:
        ifc_file = ifcopenshell.file()
        ifc_file.create_entity("IfcProject", GlobalId=ifcopenshell.guid.new(), Name="P")
        schedule = ifcopenshell.api.sequence.add_work_schedule(ifc_file, name="Schedule A")
        task = ifcopenshell.api.sequence.add_task(ifc_file, work_schedule=schedule, name="T1", identification="1")
        task_time = ifcopenshell.api.sequence.add_task_time(ifc_file, task=task)
        ifcopenshell.api.sequence.edit_task_time(
            ifc_file,
            task_time=task_time,
            attributes={"ScheduleDuration": schedule_duration},
        )
        return ifc_file

    @staticmethod
    def export(ifc_file: ifcopenshell.file) -> str:
        converter = Ifc2Msp()
        converter.file = ifc_file
        converter.work_schedule = ifc_file.by_type("IfcWorkSchedule")[0]
        with tempfile.TemporaryDirectory() as tmp_dir:
            converter.xml = str(Path(tmp_dir) / "out.xml")
            converter.execute()
            return Path(converter.xml).read_text()

    def test_sub_day_task_duration_is_not_truncated_to_zero(self):
        # Before the fix this used only duration.days, so a pure PT4H0M0S
        # duration (duration.days == 0) exported as "PT0H0M0S". Correct is
        # 4h / 24h-per-calendar-day * 8h-per-workday = 1.3333 work-hours.
        ifc_file = self.build_ifc("PT4H0M0S")
        xml = self.export(ifc_file)
        assert re.findall(r"<Duration>([^<]*)</Duration>", xml) == ["PT1H20M0S"]

    def test_mixed_day_and_hour_task_duration_keeps_the_hour_remainder(self):
        # 1 work-day (8h) + 4h = 9.3333 work-hours at 8h/day.
        ifc_file = self.build_ifc("P1DT4H0M0S")
        xml = self.export(ifc_file)
        assert re.findall(r"<Duration>([^<]*)</Duration>", xml) == ["PT9H20M0S"]
