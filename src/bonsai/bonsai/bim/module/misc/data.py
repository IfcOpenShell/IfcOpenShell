# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

from typing import Any

import bpy


def refresh() -> None:
    QuickFavoritesData.is_loaded = False


class QuickFavoritesData:
    data: dict[str, Any] = {}
    is_loaded = False

    @classmethod
    def load(cls) -> None:
        cls.data = {
            "operators": cls.operators(),
        }
        cls.is_loaded = True

    @classmethod
    def operators(cls) -> list[str]:
        items: list[str] = []
        for module_name in dir(bpy.ops):
            module = getattr(bpy.ops, module_name)
            for op_name in dir(module):
                op = getattr(module, op_name)
                bl_label = op.get_rna_type().name
                items.append(f"{module_name}.{op_name} - {bl_label}")
        return items
