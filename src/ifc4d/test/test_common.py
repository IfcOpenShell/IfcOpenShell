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

import ifcopenshell.util.sequence

from ifc4d.common import ScheduleIfcGenerator

DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday")
MONDAY = datetime.datetime(2026, 1, 19)


def at(days, hours):
    return MONDAY + datetime.timedelta(days=days, hours=hours)


def work_week(friday_finish=datetime.time(17)):
    morning = {"Start": datetime.time(8), "Finish": datetime.time(12)}
    week = []
    for day in DAYS:
        afternoon = {"Start": datetime.time(13), "Finish": friday_finish if day == "Friday" else datetime.time(17)}
        week.append({"DayOfWeek": day, "WorkTimes": [morning, afternoon], "ifc": None})
    return week


def activity(identification, calendar, hours, start, finish, **kwargs):
    return {
        "Name": f"A{identification}",
        "Identification": identification,
        "StartDate": start,
        "FinishDate": finish,
        "PlannedDuration": hours,
        "Status": "Not Started",
        "CalendarObjectId": calendar,
        "ifc": None,
        **kwargs,
    }


def generate(activities, relationships=()):
    calendars = {
        1: {"Name": "Uniform", "Type": "Global", "HoursPerDay": 8, "StandardWorkWeek": work_week()},
        # Friday from 08:00 to 15:00: 6 work hours, the other days 8 work hours.
        2: {
            "Name": "Short Friday",
            "Type": "Global",
            "HoursPerDay": 8,
            "StandardWorkWeek": work_week(datetime.time(15)),
        },
    }
    settings = {
        "work_plan": None,
        "project": {"Name": "Test"},
        "calendars": calendars,
        "wbs": {},
        "root_activities": [a["Identification"] for a in activities],
        "activities": {a["Identification"]: a for a in activities},
        "relationships": {i: r for i, r in enumerate(relationships)},
        "resources": {},
    }
    generator = ScheduleIfcGenerator(None, None, settings)
    generator.create_ifc()
    return generator


class TestDurations:
    def test_writing_whole_work_days_for_a_uniform_calendar(self):
        task = activity(1, 1, 16, at(0, 8), at(1, 17))
        generate([task])
        assert task["ifc"].TaskTime.ScheduleDuration == "P2D"

    def test_writing_work_hours_for_a_part_of_a_day(self):
        # A task of work days starts at the start of a day. Work hours are exact, as in the source.
        task = activity(1, 1, 12, at(0, 13), at(1, 17))
        generate([task])
        assert task["ifc"].TaskTime.ScheduleDuration == "PT12H"

    def test_writing_work_hours_for_a_calendar_with_days_of_different_lengths(self):
        task = activity(1, 2, 12, at(4, 8), at(7, 15))  # 6 hours on Friday, 6 hours on Monday
        generate([task])
        assert task["ifc"].TaskTime.ScheduleDuration == "PT12H"

    def test_giving_the_dates_of_the_source(self):
        task = activity(1, 2, 12, at(4, 8), at(7, 15))
        generate([task])
        task_time = task["ifc"].TaskTime
        calendar = ifcopenshell.util.sequence.derive_calendar(task["ifc"])
        duration = task_time.ScheduleDuration
        finish = ifcopenshell.util.sequence.get_start_or_finish_date(at(4, 8), duration, "WORKTIME", calendar)
        assert finish == at(7, 15)

    def test_writing_a_milestone(self):
        task = activity(1, 1, 0, at(0, 8), at(0, 8))
        generate([task])
        assert task["ifc"].TaskTime.ScheduleDuration == "P0D"


class TestLags:
    def test_writing_a_lag_in_the_calendar_of_the_successor(self):
        predecessor = activity(1, 2, 8, at(0, 8), at(0, 17))
        successor = activity(2, 1, 8, at(1, 10), at(2, 10))
        link = {"PredecessorActivity": 1, "SuccessorActivity": 2, "Type": "FINISH_START", "Lag": 16}
        generate([predecessor, successor], [link])
        # Whole days in the uniform calendar of the successor. The calendar of the predecessor would give PT16H.
        assert successor["ifc"].IsSuccessorFrom[0].TimeLag.LagValue.wrappedValue == "P2D"

    def test_writing_a_negative_lag(self):
        predecessor = activity(1, 1, 8, at(0, 8), at(0, 17))
        successor = activity(2, 2, 8, at(0, 15), at(1, 15))
        link = {"PredecessorActivity": 1, "SuccessorActivity": 2, "Type": "FINISH_START", "Lag": -2.5}
        generate([predecessor, successor], [link])
        assert successor["ifc"].IsSuccessorFrom[0].TimeLag.LagValue.wrappedValue == "-PT2H30M"


class TestFloats:
    def test_writing_floats_as_work_time(self):
        task = activity(1, 1, 8, at(0, 8), at(0, 17), TotalFloat=8, FreeFloat=4)
        generate([task])
        assert task["ifc"].TaskTime.TotalFloat == "P1D"
        assert task["ifc"].TaskTime.FreeFloat == "PT4H"
        assert task["ifc"].TaskTime.IsCritical is False

    def test_writing_floats_as_work_hours_on_a_calendar_with_days_of_different_lengths(self):
        task = activity(1, 2, 8, at(0, 8), at(0, 17), TotalFloat=16)
        generate([task])
        assert task["ifc"].TaskTime.TotalFloat == "PT16H"

    def test_writing_a_negative_float(self):
        task = activity(1, 1, 8, at(1, 8), at(1, 17), TotalFloat=-8)
        generate([task])
        assert task["ifc"].TaskTime.TotalFloat == "-P1D"
        assert task["ifc"].TaskTime.IsCritical is True


class TestCalendars:
    def test_reading_a_work_period_that_ends_at_midnight(self):
        task = activity(1, 1, 8, at(0, 8), at(0, 17))
        generator = generate([task])
        calendar = generator.calendars[1]
        calendar["StandardWorkWeek"] = [
            {"DayOfWeek": d, "WorkTimes": [{"Start": datetime.time(0), "Finish": datetime.time(0)}], "ifc": None}
            for d in DAYS
        ]
        generator.create_calendars()
        periods = ifcopenshell.util.sequence.get_work_periods(MONDAY, calendar["ifc"])
        assert periods == [(datetime.timedelta(), datetime.timedelta(days=1))]
