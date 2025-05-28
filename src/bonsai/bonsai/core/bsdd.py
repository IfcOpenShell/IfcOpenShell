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

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import bsdd
    import bonsai.tool as tool


def import_bsdd_classes(bsdd: tool.Bsdd, obj, obj_type) -> int:
    return bsdd.import_classes(obj, obj_type)


def search_bsdd_properties(bsdd: tool.Bsdd, keyword: str, obj, obj_type) -> int:
    return bsdd.import_properties(obj, obj_type, keyword)


def load_bsdd(bsdd: tool.Bsdd) -> None:
    bsdd.clear_dictionaries()
    bsdd.create_dictionaries(bsdd.get_dictionaries())


def search_bsdd_class(bsdd: tool.Bsdd, keyword: str) -> int:
    bsdd.clear_classes()
    related_entities = bsdd.get_related_ifc_entities()
    return bsdd.search_class(keyword, related_entities)
