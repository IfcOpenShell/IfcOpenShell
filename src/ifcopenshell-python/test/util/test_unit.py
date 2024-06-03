# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.api
import ifcopenshell.util.unit as subject
from math import pi


class TestConvert(test.bootstrap.IFC4):
    def test_run(self):
        assert subject.convert(1, None, "METRE", None, "METRE") == 1
        assert subject.convert(1, None, "METRE", "MILLI", "METRE") == 1000
        assert subject.convert(1000, "MILLI", "METRE", None, "METRE") == 1
        assert subject.convert(1, None, "SQUARE_METRE", None, "SQUARE_METRE") == 1
        assert subject.convert(1, None, "SQUARE_METRE", "MILLI", "SQUARE_METRE") == 1000000
        assert subject.convert(1, None, "CUBIC_METRE", "MILLI", "CUBIC_METRE") == 1000000000


class TestCalculateUnitScale(test.bootstrap.IFC4):
    def test_prefix_and_conversion_based_units_are_considered(self):
        ifcopenshell.api.run("root.create_entity", self.file, ifc_class="IfcProject")
        length = ifcopenshell.api.run("unit.add_conversion_based_unit", self.file, name="foot")
        length.ConversionFactor.UnitComponent.Prefix = "MILLI"
        ifcopenshell.api.run("unit.assign_unit", self.file, units=[length])
        assert subject.calculate_unit_scale(self.file) == 0.3048 * 0.001

        angle = ifcopenshell.api.run("unit.add_conversion_based_unit", self.file, name="degree")
        angle.ConversionFactor.UnitComponent.Prefix = "MILLI"
        ifcopenshell.api.run("unit.assign_unit", self.file, units=[angle])
        assert subject.calculate_unit_scale(self.file, "PLANEANGLEUNIT") == pi / 180 * 0.001


class TestFormatLength(test.bootstrap.IFC4):
    def test_run(self):
        assert subject.format_length(1, 1, decimal_places=0, unit_system="metric") == "1"
        assert subject.format_length(1, 1, decimal_places=2, unit_system="metric") == "1.00"
        assert subject.format_length(3, 5, decimal_places=2, unit_system="metric") == "5.00"
        assert subject.format_length(3.123, 0.01, decimal_places=2, unit_system="metric") == "3.12"

        assert subject.format_length(3, 1, unit_system="imperial", input_unit="foot") == "3'"
        assert subject.format_length(3.5, 1, unit_system="imperial", input_unit="foot") == "3' - 6\""
        assert subject.format_length(3.123, 1, unit_system="imperial", input_unit="foot") == "3' - 1\""
        assert subject.format_length(3.123, 2, unit_system="imperial", input_unit="foot") == "3' - 1 1/2\""
        assert subject.format_length(3.123, 4, unit_system="imperial", input_unit="foot") == "3' - 1 1/2\""
        assert subject.format_length(3.123, 32, unit_system="imperial", input_unit="foot") == "3' - 1 15/32\""
        assert subject.format_length(24, 1, unit_system="imperial", input_unit="inch") == "2'"
        assert subject.format_length(25.23, 1, unit_system="imperial", input_unit="inch") == "2' - 1\""
        assert subject.format_length(25.23, 4, unit_system="imperial", input_unit="inch") == "2' - 1 1/4\""

        assert subject.format_length(3, 1, unit_system="imperial", input_unit="foot", output_unit="inch") == '36"'
        assert subject.format_length(3.5, 1, unit_system="imperial", input_unit="foot", output_unit="inch") == '42"'
        assert subject.format_length(3.123, 1, unit_system="imperial", input_unit="foot", output_unit="inch") == '37"'
        assert (
            subject.format_length(3.123, 2, unit_system="imperial", input_unit="foot", output_unit="inch") == '37 1/2"'
        )
        assert (
            subject.format_length(3.123, 4, unit_system="imperial", input_unit="foot", output_unit="inch") == '37 1/2"'
        )
        assert (
            subject.format_length(3.123, 32, unit_system="imperial", input_unit="foot", output_unit="inch")
            == '37 15/32"'
        )
        assert subject.format_length(24, 1, unit_system="imperial", input_unit="inch", output_unit="inch") == '24"'
        assert subject.format_length(25.23, 1, unit_system="imperial", input_unit="inch", output_unit="inch") == '25"'
        assert (
            subject.format_length(25.23, 4, unit_system="imperial", input_unit="inch", output_unit="inch") == '25 1/4"'
        )
