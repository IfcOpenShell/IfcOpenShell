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
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import bonsai.tool as tool


def resize_to_storey(misc: tool.Misc, ifc: tool.Ifc, obj: bpy.types.Object, total_storeys: int) -> None:
    storey = misc.get_object_storey(obj)
    if not storey:
        return
    height = misc.get_storey_height_in_si(storey, total_storeys)
    if not height:
        return
    misc.set_object_origin_to_bottom(obj)
    misc.move_object_to_elevation(obj, misc.get_storey_elevation_in_si(storey))
    misc.scale_object_to_height(obj, height)
    ifc.edit(obj)
