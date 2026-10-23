# Ifc5D - IFC costing utility
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Ifc5D.
#
# Ifc5D is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ifc5D is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Ifc5D.  If not, see <http://www.gnu.org/licenses/>.

# This file was generated with the assistance of an AI coding tool.

import ifcopenshell
import ifcopenshell.api.root
import ifcopenshell.api.unit
import pytest

import ifc5d.qto


class TestAttributeQuantities:
    @pytest.mark.parametrize("ifc_class", ["IfcDoor", "IfcWindow"])
    def test_doors_and_windows_are_quantified_from_overall_size_without_geometry(self, ifc_class):
        file = ifcopenshell.file(schema="IFC4X3")
        ifcopenshell.api.root.create_entity(file, ifc_class="IfcProject", name="Test")
        millimetre = file.createIfcSIUnit(None, "LENGTHUNIT", "MILLI", "METRE")
        sqm = file.createIfcSIUnit(None, "AREAUNIT", None, "SQUARE_METRE")
        ifcopenshell.api.unit.assign_unit(file, units=[millimetre, sqm])
        element = ifcopenshell.api.root.create_entity(file, ifc_class=ifc_class)
        element.OverallWidth = 900.0
        element.OverallHeight = 2000.0

        results = ifc5d.qto.quantify(file, {element}, ifc5d.qto.rules["IFC4X3QtoBaseQuantities"])

        assert results[element][f"Qto_{ifc_class[3:]}BaseQuantities"] == {
            "Width": pytest.approx(900.0),
            "Height": pytest.approx(2000.0),
            "Area": pytest.approx(1.8),
            "Perimeter": pytest.approx(5800.0),
        }
