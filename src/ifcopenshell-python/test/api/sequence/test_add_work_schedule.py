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

# This file was generated with the assistance of an AI coding tool.

import ifcopenshell.api.sequence
import test.bootstrap


class TestAddWorkSchedule(test.bootstrap.IFC4):
    def test_add_work_schedule(self):
        self.file.create_entity("IfcProject")
        work_schedule = ifcopenshell.api.sequence.add_work_schedule(self.file, name="Schedule A")
        assert work_schedule.is_a("IfcWorkSchedule")
        assert work_schedule.Name == "Schedule A"

    def test_setting_identifier_default_for_ifc2x3(self):
        self.file.create_entity("IfcProject")
        work_schedule = ifcopenshell.api.sequence.add_work_schedule(self.file)
        if self.file.schema == "IFC2X3":
            assert work_schedule.Identifier == "X"


class TestAddWorkScheduleIFC2X3(test.bootstrap.IFC2X3, TestAddWorkSchedule):
    pass
