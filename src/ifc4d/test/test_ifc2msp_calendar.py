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

import tempfile
from pathlib import Path

import ifcopenshell
import ifcopenshell.api.sequence

from ifc4d.ifc2msp import Ifc2Msp


class TestIfc2MspCalendarWithoutWorkingTimes:
    def test_calendar_with_no_working_times_does_not_crash_the_export(self):
        # WorkingTimes is an optional attribute on IfcWorkCalendar. A calendar
        # created without any working time pattern (e.g. straight after
        # ifcopenshell.api.sequence.add_work_calendar, before any
        # add_work_time call) is valid IFC and leaves WorkingTimes as None.
        # Before the fix, auto_detect_working_week iterated it directly and
        # raised TypeError: 'NoneType' object is not iterable.
        ifc_file = ifcopenshell.file()
        ifc_file.create_entity("IfcProject", GlobalId=ifcopenshell.guid.new(), Name="P")
        work_schedule = ifcopenshell.api.sequence.add_work_schedule(ifc_file, name="Schedule A")
        calendar = ifcopenshell.api.sequence.add_work_calendar(ifc_file, name="Cal A")
        assert calendar.WorkingTimes is None
        ifcopenshell.api.sequence.add_task(ifc_file, work_schedule=work_schedule, name="T1", identification="1")

        converter = Ifc2Msp()
        converter.file = ifc_file
        converter.work_schedule = work_schedule
        with tempfile.TemporaryDirectory() as tmp_dir:
            converter.xml = str(Path(tmp_dir) / "out.xml")
            converter.execute()
            xml = Path(converter.xml).read_text()

        assert "<DayWorking>1</DayWorking>" in xml
