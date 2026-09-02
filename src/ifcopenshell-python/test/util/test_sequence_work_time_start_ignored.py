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

import datetime

import ifcopenshell.util.sequence as subject
import test.bootstrap


class TestIsDayInWorkTime(test.bootstrap.IFC4):
    def test_a_day_before_the_work_times_start_is_excluded(self):
        # Per the schema docs, Start is "0:00" of that date and Finish is
        # "24:00" of that date, so a work time with both set is only valid
        # for [Start, Finish] inclusive. A day before Start must never be
        # considered part of the work time, no matter how far before Finish.
        work_time = self.file.create_entity("IfcWorkTime", Start="2024-06-01", Finish="2024-12-31")
        day_before_start = datetime.date(2024, 1, 1)
        assert subject.is_day_in_work_time(day_before_start, work_time) is False

    def test_a_day_after_the_work_times_finish_is_excluded(self):
        work_time = self.file.create_entity("IfcWorkTime", Start="2024-06-01", Finish="2024-12-31")
        day_after_finish = datetime.date(2025, 1, 15)
        assert subject.is_day_in_work_time(day_after_finish, work_time) is False

    def test_a_day_inside_the_range_is_included(self):
        work_time = self.file.create_entity("IfcWorkTime", Start="2024-06-01", Finish="2024-12-31")
        day_in_range = datetime.date(2024, 7, 1)
        assert subject.is_day_in_work_time(day_in_range, work_time) is True

    def test_the_start_and_finish_days_themselves_are_included(self):
        work_time = self.file.create_entity("IfcWorkTime", Start="2024-06-01", Finish="2024-12-31")
        assert subject.is_day_in_work_time(datetime.date(2024, 6, 1), work_time) is True
        assert subject.is_day_in_work_time(datetime.date(2024, 12, 31), work_time) is True
