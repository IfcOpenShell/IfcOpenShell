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

import importlib
import inspect

import bpy
import pytest

pytestmark = pytest.mark.misc


def get_operators_without_tooltip(module_name: str) -> list[str]:
    module = importlib.import_module(f"bonsai.bim.module.{module_name}.operator")
    operators = [
        cls
        for cls in vars(module).values()
        if inspect.isclass(cls) and issubclass(cls, bpy.types.Operator) and cls.__module__ == module.__name__
    ]
    return [
        cls.bl_idname for cls in operators if not getattr(cls, "bl_description", "") and "description" not in vars(cls)
    ]


class TestOperatorTooltips:
    @pytest.mark.parametrize("module_name", ["classification", "document", "group", "layer", "library", "unit"])
    def test_every_operator_explains_itself_on_hover(self, module_name):
        assert get_operators_without_tooltip(module_name) == []
