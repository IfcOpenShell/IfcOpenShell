# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2024 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.util.cost
import test.bootstrap


class TestCopyCostSchedule(test.bootstrap.IFC4):
    def test_run(self):
        # Shared code logic with test_copy_work_schedule.
        schedule = ifcopenshell.api.cost.add_cost_schedule(self.file, name="Foo")
        item = ifcopenshell.api.cost.add_cost_item(self.file, cost_schedule=schedule)
        ifcopenshell.api.cost.add_cost_item(self.file, cost_item=item)  # Subitem.
        old_cost_items = set(self.file.by_type("IfcCostItem"))

        new_schedule = ifcopenshell.api.cost.copy_cost_schedule(self.file, schedule)

        # We don't check how well IfcCostItems are copied,
        # it should be tested separately in test_copy_cost_item.
        assert isinstance(new_schedule, ifcopenshell.entity_instance)
        assert new_schedule != schedule
        assert len(ifcopenshell.util.cost.get_root_cost_items(new_schedule)) == 1
        new_cost_items = set(ifcopenshell.util.cost.get_schedule_cost_items(new_schedule))
        assert len(new_cost_items) == 2
        assert len(new_cost_items.intersection(old_cost_items)) == 0


class TestCopyCostScheduleIFC2X3(test.bootstrap.IFC2X3, TestCopyCostSchedule):
    pass


class TestCopyCostScheduleIFC4X3(test.bootstrap.IFC4X3, TestCopyCostSchedule):
    pass
