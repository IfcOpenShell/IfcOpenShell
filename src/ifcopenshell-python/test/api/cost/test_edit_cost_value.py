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
import ifcopenshell.api.unit
import test.bootstrap


class TestEditCostValue(test.bootstrap.IFC4):
    def test_editing_applied_value(self):
        schedule = ifcopenshell.api.cost.add_cost_schedule(self.file)
        item = ifcopenshell.api.cost.add_cost_item(self.file, cost_schedule=schedule)
        value = ifcopenshell.api.cost.add_cost_value(self.file, parent=item)
        ifcopenshell.api.cost.edit_cost_value(self.file, cost_value=value, attributes={"AppliedValue": 42.0})
        assert value.AppliedValue.wrappedValue == 42.0

    def test_editing_unit_basis_removes_old_deeply(self):
        schedule = ifcopenshell.api.cost.add_cost_schedule(self.file)
        item = ifcopenshell.api.cost.add_cost_item(self.file, cost_schedule=schedule)
        value = ifcopenshell.api.cost.add_cost_value(self.file, parent=item)
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT")
        ifcopenshell.api.cost.edit_cost_value(
            self.file,
            cost_value=value,
            attributes={"UnitBasis": {"ValueComponent": 1.0, "UnitComponent": unit}},
        )
        old_basis = value.UnitBasis
        assert old_basis is not None
        old_basis_id = old_basis.id()
        # Now change to a new unit basis — the old one should be deeply removed.
        ifcopenshell.api.cost.edit_cost_value(
            self.file,
            cost_value=value,
            attributes={"UnitBasis": {"ValueComponent": 2.0, "UnitComponent": unit}},
        )
        assert value.UnitBasis is not None
        assert value.UnitBasis.id() != old_basis_id

    def test_clearing_unit_basis(self):
        schedule = ifcopenshell.api.cost.add_cost_schedule(self.file)
        item = ifcopenshell.api.cost.add_cost_item(self.file, cost_schedule=schedule)
        value = ifcopenshell.api.cost.add_cost_value(self.file, parent=item)
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT")
        ifcopenshell.api.cost.edit_cost_value(
            self.file,
            cost_value=value,
            attributes={"UnitBasis": {"ValueComponent": 1.0, "UnitComponent": unit}},
        )
        assert value.UnitBasis is not None
        ifcopenshell.api.cost.edit_cost_value(self.file, cost_value=value, attributes={"UnitBasis": None})
        assert value.UnitBasis is None


class TestEditCostValueIFC4X3(test.bootstrap.IFC4X3, TestEditCostValue):
    pass
