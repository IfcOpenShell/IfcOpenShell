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

import ifcopenshell.api.cost
import ifcopenshell.api.root
import test.bootstrap
import ifcopenshell.api
import ifcopenshell.api.control
import ifcopenshell.api.sequence
import ifcopenshell.util.element
from datetime import datetime
from typing import Union


def deprecation_check(test):
    def new_test(self):
        assert datetime.now().date() < datetime(2026, 1, 9).date(), "API arguments are completely deprecated"
        test(self)

    return new_test


class TestTemporarySupportForDeprecatedAPIArguments(test.bootstrap.IFC4):
    @deprecation_check
    def test_assigning_control(self):
        model = self.file
        element = ifcopenshell.api.root.create_entity(model, ifc_class="IfcWall")
        control = ifcopenshell.api.cost.add_cost_schedule(model)
        ifcopenshell.api.control.assign_control(model, relating_control=control, related_objects=[element])
        assert list(ifcopenshell.util.element.get_controls(element)) == [control]

    @deprecation_check
    def test_unassigning_control(self):
        TestTemporarySupportForDeprecatedAPIArguments.test_assigning_control(self)
        model = self.file
        element = model.by_type("IfcWall")[0]
        control = model.by_type("IfcCostSchedule")[0]
        ifcopenshell.api.control.unassign_control(model, relating_control=control, related_objects=[element])
        assert list(ifcopenshell.util.element.get_controls(element)) == []
