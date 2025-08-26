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

import test.bootstrap
import ifcopenshell.api.cost
import ifcopenshell.api.root
import ifcopenshell.api.control


class TestAddCostItemQuantity(test.bootstrap.IFC4):
    def test_run(self):
        schema = ifcopenshell.schema_by_name(self.file.schema)
        assert (entity := schema.declaration_by_name("IfcPhysicalSimpleQuantity").as_entity())
        quantity_types = [t.name() for t in entity.subtypes()]
        schedule = ifcopenshell.api.cost.add_cost_schedule(self.file)
        item = ifcopenshell.api.cost.add_cost_item(self.file, cost_schedule=schedule)
        wall = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")
        ifcopenshell.api.control.assign_control(self.file, relating_control=item, related_object=wall)

        quantities = []
        for quantity_type in quantity_types:
            quantity = ifcopenshell.api.cost.add_cost_item_quantity(self.file, cost_item=item, ifc_class=quantity_type)
            assert quantity.is_a(quantity_type)
            assert quantity.Name == "Unnamed"
            if quantity_type == "IfcQuantityCount":
                assert quantity[3] == 1
            else:
                assert quantity[3] == 0.0
            quantities.append(quantity)
        assert item.CostQuantities == tuple(quantities)


# CostQuantities was added to IfcCostItem in IFC4.
class TestAddCostItemQuantityIFC4X3(test.bootstrap.IFC4X3, TestAddCostItemQuantity):
    pass
