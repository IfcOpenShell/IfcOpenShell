# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026
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

import ifcopenshell.api.sequence
import test.bootstrap


class TestAssignLagTime(test.bootstrap.IFC4):
    def test_assigning_a_percentage_lag(self):
        predecessor = self.file.createIfcTask()
        successor = self.file.createIfcTask()
        rel_sequence = ifcopenshell.api.sequence.assign_sequence(
            self.file, relating_process=predecessor, related_process=successor
        )

        lag_time = ifcopenshell.api.sequence.assign_lag_time(self.file, rel_sequence=rel_sequence, lag_value=0.5)

        assert rel_sequence.TimeLag == lag_time
        assert lag_time.LagValue.is_a("IfcRatioMeasure")
        assert lag_time.LagValue.wrappedValue == 0.5


class TestAssignLagTimeIFC4X3(test.bootstrap.IFC4X3, TestAssignLagTime):
    pass
