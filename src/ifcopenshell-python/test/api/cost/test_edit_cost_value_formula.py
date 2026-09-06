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

import ifcopenshell.api.cost
import test.bootstrap


class TestEditCostValueFormula(test.bootstrap.IFC4):
    def test_setting_an_explicit_zero_value(self):
        schedule = ifcopenshell.api.cost.add_cost_schedule(self.file)
        item = ifcopenshell.api.cost.add_cost_item(self.file, cost_schedule=schedule)
        value = ifcopenshell.api.cost.add_cost_value(self.file, parent=item)

        # A formula of exactly "0" is a legitimate, explicit cost of zero
        # (e.g. "included at no extra cost"). It must not be silently
        # dropped down to an unset (None) applied value.
        ifcopenshell.api.cost.edit_cost_value_formula(self.file, cost_value=value, formula="0")
        assert value.AppliedValue is not None
        assert value.AppliedValue.wrappedValue == 0.0

    def test_setting_a_non_zero_value(self):
        schedule = ifcopenshell.api.cost.add_cost_schedule(self.file)
        item = ifcopenshell.api.cost.add_cost_item(self.file, cost_schedule=schedule)
        value = ifcopenshell.api.cost.add_cost_value(self.file, parent=item)

        ifcopenshell.api.cost.edit_cost_value_formula(self.file, cost_value=value, formula="42")
        assert value.AppliedValue.wrappedValue == 42.0

    def test_clearing_a_value_with_a_blank_formula(self):
        schedule = ifcopenshell.api.cost.add_cost_schedule(self.file)
        item = ifcopenshell.api.cost.add_cost_item(self.file, cost_schedule=schedule)
        value = ifcopenshell.api.cost.add_cost_value(self.file, parent=item)

        ifcopenshell.api.cost.edit_cost_value_formula(self.file, cost_value=value, formula="42")
        assert value.AppliedValue is not None

        # An intentionally blank formula clears the applied value back to unset.
        ifcopenshell.api.cost.edit_cost_value_formula(self.file, cost_value=value, formula="")
        assert value.AppliedValue is None
