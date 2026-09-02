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

import ifcopenshell

from ifc4d.p6xer2ifc import P6XER2Ifc


# Minimal stand-ins for xerparser's Calendar/Exception rows. p6xer2ifc.py
# only reads .clndr_id/.clndr_name/.clndr_type/.day_hr_cnt/.working_hours/
# .exceptions off a calendar, and .year/.month/.day off an exception.
class FakeException:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day


class FakeCalendar:
    def __init__(self, clndr_id, clndr_name, exceptions):
        self.clndr_id = clndr_id
        self.clndr_name = clndr_name
        self.clndr_type = "CA_Base"
        self.day_hr_cnt = 8
        self.working_hours = []
        self.exceptions = exceptions


class FakeModel:
    def __init__(self, calendars):
        self.calendars = calendars


class TestParseCalendarXerExceptionsAreNotShared:
    @staticmethod
    def parse_two_calendars() -> P6XER2Ifc:
        p6xer2ifc = P6XER2Ifc()
        p6xer2ifc.model = FakeModel(
            [
                FakeCalendar("CAL_A", "Calendar A", [FakeException(2024, 1, 1)]),
                FakeCalendar("CAL_B", "Calendar B", [FakeException(2024, 12, 25)]),
            ]
        )
        p6xer2ifc.parse_calendar_xer()
        return p6xer2ifc

    def test_each_calendar_gets_its_own_exceptions_dict(self):
        p6xer2ifc = self.parse_two_calendars()
        cal_a_exceptions = p6xer2ifc.calendars["CAL_A"]["HolidayOrExceptions"]
        cal_b_exceptions = p6xer2ifc.calendars["CAL_B"]["HolidayOrExceptions"]
        # Before the fix, both calendars pointed at the exact same dict
        # object (exceptions = {} was declared outside the per-calendar
        # loop), so every calendar ended up with the union of every other
        # calendar's holidays.
        assert cal_a_exceptions is not cal_b_exceptions

    def test_calendar_a_only_has_its_own_holiday(self):
        p6xer2ifc = self.parse_two_calendars()
        cal_a_exceptions = p6xer2ifc.calendars["CAL_A"]["HolidayOrExceptions"]
        assert cal_a_exceptions == {2024: {1: {"FullDay": [1], "WorkTime": []}}}

    def test_calendar_b_only_has_its_own_holiday(self):
        p6xer2ifc = self.parse_two_calendars()
        cal_b_exceptions = p6xer2ifc.calendars["CAL_B"]["HolidayOrExceptions"]
        assert cal_b_exceptions == {2024: {12: {"FullDay": [25], "WorkTime": []}}}


class TestCreateCalendarsDoesNotCrossContaminateExceptionTimes:
    @staticmethod
    def build_ifc() -> ifcopenshell.file:
        from ifc4d.common import ScheduleIfcGenerator

        p6xer2ifc = TestParseCalendarXerExceptionsAreNotShared.parse_two_calendars()
        p6xer2ifc.project["Name"] = "Test Project"
        ifc_file = ifcopenshell.file(schema="IFC4")
        ifc_file.create_entity("IfcProject", GlobalId=ifcopenshell.guid.new(), Name="P")
        settings = {
            "work_plan": p6xer2ifc.work_plan,
            "project": p6xer2ifc.project,
            "calendars": p6xer2ifc.calendars,
            "wbs": p6xer2ifc.wbs,
            "root_activities": p6xer2ifc.root_activites,
            "activities": p6xer2ifc.activities,
            "relationships": p6xer2ifc.relationships,
            "resources": p6xer2ifc.resources,
        }
        generator = ScheduleIfcGenerator(ifc_file, None, settings)
        generator.create_ifc()
        return ifc_file

    @staticmethod
    def get_exception_days(calendar: ifcopenshell.entity_instance) -> set[tuple[int, int]]:
        days = set()
        for work_time in calendar.ExceptionTimes or []:
            pattern = work_time.RecurrencePattern
            for month in pattern.MonthComponent:
                for day in pattern.DayComponent:
                    days.add((month, day))
        return days

    def test_each_ifc_work_calendar_only_gets_its_own_holiday(self):
        ifc_file = self.build_ifc()
        calendars = {c.Identification: c for c in ifc_file.by_type("IfcWorkCalendar")}
        assert self.get_exception_days(calendars["CAL_A"]) == {(1, 1)}
        assert self.get_exception_days(calendars["CAL_B"]) == {(12, 25)}
