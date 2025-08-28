# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell.util
import ifcopenshell.util.date
import test.bootstrap
import ifcopenshell.api.sequence
from datetime import datetime


class TestAddDateTime(test.bootstrap.IFC4):
    def test_run(self):
        dt = datetime(2025, 3, 1, 12, 31, 24)
        res = ifcopenshell.api.sequence.add_date_time(self.file, dt)
        if self.file.schema == "IFC2X3":
            assert isinstance(res, ifcopenshell.entity_instance)
            assert res.is_a("IfcDateAndTime")
            assert ifcopenshell.util.date.ifc2datetime(res) == dt
            print(res)
        else:
            assert res == "2025-03-01T12:31:24"


class TestAddDateTimeIFC2X3(test.bootstrap.IFC2X3, TestAddDateTime):
    pass


class TestAddDateTimeIFC4X3(test.bootstrap.IFC4X3, TestAddDateTime):
    pass
