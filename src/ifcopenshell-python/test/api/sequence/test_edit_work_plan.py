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

import datetime

import ifcopenshell.api.sequence
import test.bootstrap


class TestEditWorkPlan(test.bootstrap.IFC4):
    def test_editing_duration_to_a_zero_length_value(self):
        self.file.create_entity("IfcProject")
        work_plan = ifcopenshell.api.sequence.add_work_plan(self.file)

        ifcopenshell.api.sequence.edit_work_plan(
            self.file, work_plan=work_plan, attributes={"Duration": datetime.timedelta(0)}
        )
        assert work_plan.Duration == "P0D"

    def test_editing_duration_to_none_clears_it(self):
        self.file.create_entity("IfcProject")
        work_plan = ifcopenshell.api.sequence.add_work_plan(self.file)

        ifcopenshell.api.sequence.edit_work_plan(self.file, work_plan=work_plan, attributes={"Duration": "P2D"})
        assert work_plan.Duration == "P2D"

        ifcopenshell.api.sequence.edit_work_plan(self.file, work_plan=work_plan, attributes={"Duration": None})
        assert work_plan.Duration is None
