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

import pytest
import test.bootstrap
import ifcopenshell.api
import ifcopenshell.util.unit as subject


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
