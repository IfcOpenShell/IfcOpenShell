# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

import ifcopenshell.api.cost
import ifcopenshell.guid
import ifcopenshell.validate
import test.bootstrap


class TestRemoveCostItemQuantity(test.bootstrap.IFC4):
    def test_removing_the_last_quantity_leaves_a_valid_cost_item(self):
        schedule = ifcopenshell.api.cost.add_cost_schedule(self.file)
        item = ifcopenshell.api.cost.add_cost_item(self.file, cost_schedule=schedule)
        quantity = ifcopenshell.api.cost.add_cost_item_quantity(
            self.file, cost_item=item, ifc_class="IfcQuantityVolume"
        )
        # Give the quantity a second inverse so it is not simply purged, and
        # the CostQuantities-emptying branch is exercised instead.
        self.file.create_entity("IfcElementQuantity", GlobalId=ifcopenshell.guid.new(), Quantities=[quantity])
        assert item.CostQuantities

        ifcopenshell.api.cost.remove_cost_item_quantity(self.file, cost_item=item, physical_quantity=quantity)

        # An empty list is not a valid value: CostQuantities is either unset
        # or has at least one member.
        assert item.CostQuantities is None

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(self.file, logger)
        assert not logger.statements, logger.statements

    def test_removing_one_of_several_quantities_keeps_the_others(self):
        schedule = ifcopenshell.api.cost.add_cost_schedule(self.file)
        item = ifcopenshell.api.cost.add_cost_item(self.file, cost_schedule=schedule)
        quantity1 = ifcopenshell.api.cost.add_cost_item_quantity(
            self.file, cost_item=item, ifc_class="IfcQuantityVolume"
        )
        quantity2 = ifcopenshell.api.cost.add_cost_item_quantity(self.file, cost_item=item, ifc_class="IfcQuantityArea")
        self.file.create_entity("IfcElementQuantity", GlobalId=ifcopenshell.guid.new(), Quantities=[quantity1])

        ifcopenshell.api.cost.remove_cost_item_quantity(self.file, cost_item=item, physical_quantity=quantity1)

        assert item.CostQuantities == (quantity2,)
