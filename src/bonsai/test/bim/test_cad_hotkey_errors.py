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

from unittest.mock import MagicMock

from bonsai.bim.module.cad.workspace import CadHotkey
from test.bim.bootstrap import NewFile


def raise_nested_operator_error():
    raise RuntimeError("Error: Exactly 2 vertices should be selected.")


class TestCadHotkey(NewFile):
    def test_nested_operator_error_is_reported_instead_of_raised(self):
        operator = MagicMock(hotkey="S_C", hotkey_S_C=raise_nested_operator_error)
        result = CadHotkey.execute(operator, MagicMock())
        assert result == {"CANCELLED"}
        operator.report.assert_called_once_with({"ERROR"}, "Exactly 2 vertices should be selected.")
