# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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

# This file was generated with the assistance of an AI coding tool.

import pytest

import bonsai.tool as tool
from bonsai.bim.module.material.ui import get_material_filter_flags

FLAG = 1


def add_category(materials, name):
    category = materials.add()
    category["name"] = name
    category.is_category = True


def add_material(materials, name):
    material = materials.add()
    material["name"] = name


@pytest.mark.parametrize(
    "filter_name,expected_flags",
    [
        ("c30", [FLAG, FLAG, 0, 0]),
        (" C30 ", [FLAG, FLAG, 0, 0]),
        ("CONCRETE", [FLAG, 0, 0, 0]),
        ("steel", [0, 0, FLAG, 0]),
        ("s235", [0, 0, FLAG, FLAG]),
        ("zzz", [0, 0, 0, 0]),
    ],
)
def test_get_material_filter_flags(filter_name, expected_flags):
    materials = tool.Material.get_material_props().materials
    materials.clear()
    add_category(materials, "Concrete")
    add_material(materials, "C30/37")
    add_category(materials, "Steel")
    add_material(materials, "S235")

    assert get_material_filter_flags(materials, filter_name, FLAG) == expected_flags
