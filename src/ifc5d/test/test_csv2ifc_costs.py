# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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


import ifcopenshell
import ifcopenshell.api.cost
import ifcopenshell.api.root
import ifcopenshell.api.unit
import pytest

import ifc5d.csv2ifc
import ifc5d.ifc5Dspreadsheet


class TestCostCategoryTotals:
    def test_two_cost_values_sharing_a_category_are_summed_not_overwritten(self):
        ifc_file = ifcopenshell.file()
        ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject", name="Test")
        ifcopenshell.api.unit.assign_unit(ifc_file)
        schedule = ifcopenshell.api.cost.add_cost_schedule(ifc_file, name="Sched")
        item = ifcopenshell.api.cost.add_cost_item(ifc_file, cost_schedule=schedule)
        item.Name = "Wall"

        value1 = ifcopenshell.api.cost.add_cost_value(ifc_file, parent=item)
        value1.AppliedValue = ifc_file.create_entity("IfcMonetaryMeasure", 100.0)
        value2 = ifcopenshell.api.cost.add_cost_value(ifc_file, parent=item)
        value2.AppliedValue = ifc_file.create_entity("IfcMonetaryMeasure", 250.0)

        data = ifc5d.ifc5Dspreadsheet.IfcDataGetter.get_cost_items_data(ifc_file, item)[0]

        assert data["RateSubtotal"] == pytest.approx(350.0)
        assert data["cost_categories"]["General Cost"] == pytest.approx(350.0)


class TestLocaleIndependentCostValueImport:
    def test_category_cost_values_parse_with_plain_float_not_locale_atof(self, monkeypatch):
        import locale

        def fail_if_called(*args, **kwargs):
            raise AssertionError("locale.atof() must not be used to parse cost values")

        monkeypatch.setattr(locale, "atof", fail_if_called)

        importer = ifc5d.csv2ifc.Csv2Ifc(csv=None)
        importer.has_categories = True
        importer.has_rates = False
        importer.has_formula = False
        importer.categories = {"Material": 4}
        importer.headers = {"Name": 0, "Unit": 1, "Identification": 2, "Description": 3, "Material Cost": 4}

        row = ["Wall", "unit", "1", "", "1234.56"]
        cost_data = importer.get_row_cost_data(row)

        assert cost_data["CostValues"] == {"Material": 1234.56}
