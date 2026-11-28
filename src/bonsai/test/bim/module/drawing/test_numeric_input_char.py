# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
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
#
# This file was generated with the assistance of an AI coding tool.

from types import SimpleNamespace

import pytest

from bonsai.bim.module.drawing.gizmos import resolve_numeric_input_char


def _event(type, ascii, value="PRESS"):
    return SimpleNamespace(type=type, ascii=ascii, value=value)


@pytest.mark.parametrize("ascii", [",", "."])
def test_numpad_decimal_key_gives_a_dot_whatever_it_emits(ascii):
    assert resolve_numeric_input_char(_event("NUMPAD_PERIOD", ascii)) == "."


def test_digit_is_passed_through():
    assert resolve_numeric_input_char(_event("NINE", "9")) == "9"


def test_typed_comma_is_not_a_decimal_separator():
    assert resolve_numeric_input_char(_event("COMMA", ",")) is None


def test_release_is_ignored():
    assert resolve_numeric_input_char(_event("NUMPAD_PERIOD", ".", value="RELEASE")) is None
