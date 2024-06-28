# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import datetime
import test.bootstrap
import ifcopenshell.api.sequence


# NOTE: IfcWorkTime was introduced in IFC4
class TestEditWorkTime(test.bootstrap.IFC4):
    def test_run(self):
        work_time = self.file.createIfcWorkTime()
        recurrence_pattern = self.file.createIfcRecurrencePattern()
        attributes = {
            "Name": "Test",
            "DataOrigin": "USERDEFINED",
            "UserDefinedDataOrigin": "Custom",
            "RecurrencePattern": recurrence_pattern,
            "Start": datetime.datetime(2020, 1, 1),
            "Finish": datetime.datetime(2020, 2, 1),
        }
        ifcopenshell.api.sequence.edit_work_time(self.file, work_time=work_time, attributes=attributes)
        assert work_time.Name == attributes["Name"]
        assert work_time.DataOrigin == attributes["DataOrigin"]
        assert work_time.UserDefinedDataOrigin == attributes["UserDefinedDataOrigin"]
        assert work_time.RecurrencePattern == attributes["RecurrencePattern"]
        assert work_time[4] == "2020-01-01"
        assert work_time[5] == "2020-02-01"


class TestEditWorkTimeIFC4X3(test.bootstrap.IFC4X3):
    def test_run(self):
        work_time = self.file.createIfcWorkTime()
        recurrence_pattern = self.file.createIfcRecurrencePattern()
        attributes = {
            "Name": "Test",
            "DataOrigin": "USERDEFINED",
            "UserDefinedDataOrigin": "Custom",
            "RecurrencePattern": recurrence_pattern,
            "StartDate": datetime.datetime(2020, 1, 1),
            "FinishDate": datetime.datetime(2020, 2, 1),
        }
        ifcopenshell.api.sequence.edit_work_time(self.file, work_time=work_time, attributes=attributes)
        assert work_time.Name == attributes["Name"]
        assert work_time.DataOrigin == attributes["DataOrigin"]
        assert work_time.UserDefinedDataOrigin == attributes["UserDefinedDataOrigin"]
        assert work_time.RecurrencePattern == attributes["RecurrencePattern"]
        assert work_time.StartDate == "2020-01-01"
        assert work_time.FinishDate == "2020-02-01"

    def test_ifc4_code_to_work_in_ifc4x3(self):
        TestEditWorkTime.test_run(self)
