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
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.validate
import test.bootstrap


class TestUnassignCostItemQuantity(test.bootstrap.IFC4):
    def test_unassigning_the_last_quantity_leaves_a_valid_cost_item(self):
        schedule = ifcopenshell.api.cost.add_cost_schedule(self.file)
        item = ifcopenshell.api.cost.add_cost_item(self.file, cost_schedule=schedule)
        slab = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcSlab")
        qto = ifcopenshell.api.pset.add_qto(self.file, product=slab, name="Qto_SlabBaseQuantities")
        ifcopenshell.api.pset.edit_qto(self.file, qto=qto, properties={"NetVolume": 42.0})
        ifcopenshell.api.cost.assign_cost_item_quantity(
            self.file, cost_item=item, products=[slab], prop_name="NetVolume"
        )
        assert item.CostQuantities

        ifcopenshell.api.cost.unassign_cost_item_quantity(self.file, cost_item=item, products=[slab])

        # An empty list is not a valid value: CostQuantities is either unset
        # or has at least one member.
        assert item.CostQuantities is None

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(self.file, logger)
        assert not logger.statements, logger.statements
