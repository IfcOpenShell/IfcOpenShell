# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

from unittest.mock import patch

from bonsai.bim.prop import get_float_string_value, set_float_string_value
from test.bim.bootstrap import NewFile


class FakeAttribute(dict):
    data_type = "float"
    value_min_constraint = False
    value_max_constraint = False
    value_min = 0.0
    value_max = 0.0

    def get_value_name(self, display_only: bool = False):
        if self.data_type == "float":
            return "float_string_value" if display_only else "float_value"
        return "float_value"


class TestAttributeFloatPrecision(NewFile):
    def test_display_value_name_is_float_string_value(self):
        attr = FakeAttribute()
        assert attr.get_value_name(display_only=True) == "float_string_value"
        assert attr.get_value_name(display_only=False) == "float_value"

    def test_preserves_double_precision_float_values(self):
        attr = FakeAttribute()
        with patch("bonsai.bim.prop.update_attribute_value"):
            set_float_string_value(attr, "320.15")
            assert attr["float_value"] == 320.15
            assert get_float_string_value(attr) == "320.15"

            set_float_string_value(attr, "1234567.891")
            assert attr["float_value"] == 1234567.891
            assert get_float_string_value(attr) == "1234567.891"

            set_float_string_value(attr, "not_a_number")
            assert attr["float_value"] == 1234567.891
