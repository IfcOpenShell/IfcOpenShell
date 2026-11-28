# Ifc4D - IFC scheduling utility
# Copyright (C) 2026 myoualid
#
# This file is part of Ifc4D.
#
# Ifc4D is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ifc4D is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Ifc4D.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

import datetime
import xml.etree.ElementTree as ET

import ifcopenshell
import ifcopenshell.api.control
import ifcopenshell.api.root
import ifcopenshell.api.sequence as sequence
import ifcopenshell.util.sequence

import ifc4d.common
from ifc4d.ifc2msp import Ifc2Msp
from ifc4d.ifc2p6 import Ifc2P6


def create_schedule():
    """Tasks in a calendar with a short Friday: 08:00 to 15:00, the other days 08:00 to 17:00"""
    file = ifcopenshell.file(schema="IFC4")
    ifcopenshell.api.root.create_entity(file, ifc_class="IfcProject")
    work_schedule = sequence.add_work_schedule(file)
    calendar = sequence.add_work_calendar(file)
    for weekdays, finish in (([1, 2, 3, 4], "17:00"), ([5], "15:00")):
        work_time = sequence.add_work_time(file, work_calendar=calendar)
        pattern = sequence.assign_recurrence_pattern(file, parent=work_time, recurrence_type="WEEKLY")
        sequence.edit_recurrence_pattern(file, recurrence_pattern=pattern, attributes={"WeekdayComponent": weekdays})
        sequence.add_time_period(file, recurrence_pattern=pattern, start_time="08:00", end_time="12:00")
        sequence.add_time_period(file, recurrence_pattern=pattern, start_time="13:00", end_time=finish)
    tasks = {}
    for name, duration, duration_type, start in (
        ("A", "PT12H", "WORKTIME", "2026-01-23T08:00:00"),  # Friday 08:00 to Monday 15:00
        ("B", "P1DT4H", "WORKTIME", "2026-01-19T08:00:00"),  # Monday 08:00 to Tuesday 12:00
        ("C", "P1D", "ELAPSEDTIME", "2026-01-19T08:00:00"),  # Monday 08:00 to Tuesday 08:00
        ("D", "P1D", "WORKTIME", "2026-01-26T08:00:00"),
        ("E", "P1D", "WORKTIME", "2026-01-26T08:00:00"),
    ):
        task = sequence.add_task(file, work_schedule=work_schedule, name=name, identification=name)
        ifcopenshell.api.control.assign_control(file, relating_control=calendar, related_objects=[task])
        task_time = sequence.add_task_time(file, task=task)
        attributes = {"ScheduleStart": start, "ScheduleDuration": duration, "DurationType": duration_type}
        sequence.edit_task_time(file, task_time=task_time, attributes=attributes)
        tasks[name] = task
    # B finishes on Tuesday at 12:00, the middle of the day. P1D later is the middle of Wednesday: 8 work hours.
    rel = sequence.assign_sequence(file, relating_process=tasks["B"], related_process=tasks["D"])
    sequence.assign_lag_time(file, rel_sequence=rel, lag_value="P1D", duration_type="WORKTIME")
    # A ratio of the 12 work hours of A.
    rel = sequence.assign_sequence(file, relating_process=tasks["A"], related_process=tasks["E"])
    rel.TimeLag = file.createIfcLagTime(DurationType="WORKTIME", LagValue=file.createIfcRatioMeasure(0.5))
    return file, work_schedule, tasks


def test_task_work_hours_give_the_dates_of_the_schedule():
    file, work_schedule, tasks = create_schedule()
    assert tasks["A"].TaskTime.ScheduleFinish == "2026-01-26T15:00:00"
    assert ifc4d.common.get_task_work_hours(tasks["A"]) == 12
    assert ifc4d.common.get_task_work_hours(tasks["B"]) == 12
    assert ifc4d.common.get_task_work_hours(tasks["C"]) == 8  # Elapsed time: the work hours of the dates


def test_exporting_work_hours_to_p6(tmp_path):
    file, work_schedule, tasks = create_schedule()
    exporter = Ifc2P6()
    exporter.file = file
    exporter.xml = str(tmp_path / "schedule.xml")
    exporter.holiday_start_date = datetime.date(2026, 1, 1)
    exporter.holiday_finish_date = datetime.date(2026, 2, 1)
    exporter.execute()
    root = ET.parse(exporter.xml).getroot()
    ns = {"p6": root.tag[1:].partition("}")[0]}
    durations = {
        a.findtext("p6:Id", namespaces=ns): a.findtext("p6:PlannedDuration", namespaces=ns)
        for a in root.iter(f"{{{ns['p6']}}}Activity")
    }
    assert durations["A"] == "12"
    assert durations["B"] == "12"
    lags = sorted(r.findtext("p6:Lag", namespaces=ns) for r in root.iter(f"{{{ns['p6']}}}Relationship"))
    assert lags == ["6", "8"]


def test_exporting_work_hours_to_ms_project(tmp_path):
    file, work_schedule, tasks = create_schedule()
    exporter = Ifc2Msp()
    exporter.file = file
    exporter.xml = str(tmp_path / "schedule.xml")
    exporter.work_schedule = work_schedule
    exporter.holiday_start_date = datetime.date(2026, 1, 1)
    exporter.holiday_finish_date = datetime.date(2026, 2, 1)
    exporter.execute()
    root = ET.parse(exporter.xml).getroot()
    ns = {"m": "http://schemas.microsoft.com/project"}
    durations = {
        t.findtext("m:Name", namespaces=ns): t.findtext("m:Duration", namespaces=ns)
        for t in root.iter(f"{{{ns['m']}}}Task")
    }
    assert durations["A"] == "PT12H0M0S"
    assert durations["B"] == "PT12H0M0S"
    assert durations["C"] == "PT8H0M0S"
    lags = sorted(int(link.findtext("m:LinkLag", namespaces=ns)) for link in root.iter(f"{{{ns['m']}}}PredecessorLink"))
    assert lags == [6 * 600, 8 * 600]
