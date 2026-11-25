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

import ifcopenshell
import ifcopenshell.api.root

from ifc4d.csv4d2ifc import Csv2Ifc

HEADER = "Hierarchy,Identification,Name,ScheduleStart,ScheduleFinish,ScheduleDuration,ActualStart,ActualFinish,ActualDuration,Relationships\n"


def convert(tmp_path, rows):
    path = tmp_path / "schedule.csv"
    path.write_text(HEADER + "".join(row + "\n" for row in rows), encoding="ISO-8859-1")
    converter = Csv2Ifc()
    converter.csv = str(path)
    converter.file = ifcopenshell.file(schema="IFC4")
    ifcopenshell.api.root.create_entity(converter.file, ifc_class="IfcProject")
    converter.execute()
    return {t.Identification: t.TaskTime for t in converter.file.by_type("IfcTask")}


def test_giving_a_date_without_a_time_the_first_work_instant(tmp_path):
    times = convert(tmp_path, ["1,1,A,2026-01-19,,2d,,,,"])
    assert times["1"].ScheduleStart == "2026-01-19T09:00:00"
    assert times["1"].ScheduleFinish == "2026-01-20T17:00:00"


def test_keeping_a_given_time(tmp_path):
    times = convert(tmp_path, ["1,1,A,2026-01-19T13:00:00,,4h,,,,"])
    assert times["1"].ScheduleStart == "2026-01-19T13:00:00"
    assert times["1"].ScheduleFinish == "2026-01-19T17:00:00"


def test_giving_a_finish_date_without_a_time_the_last_work_instant(tmp_path):
    times = convert(tmp_path, ["1,1,A,2026-01-19,2026-01-20,,,,,"])
    assert times["1"].ScheduleFinish == "2026-01-20T17:00:00"
    assert times["1"].ScheduleDuration == "P2D"


def test_reading_a_part_of_a_day_as_work_hours():
    converter = Csv2Ifc()
    assert converter.parse_duration("1.5d", 8) == "P1DT4H"
    assert converter.parse_duration("1d4h", 8) == "P1DT4H"
    assert converter.parse_duration("30h", 8) == "PT30H"
    assert converter.parse_duration("2d", 8) == "P2D"
    assert converter.parse_duration("45m", 8) == "PT45M"
