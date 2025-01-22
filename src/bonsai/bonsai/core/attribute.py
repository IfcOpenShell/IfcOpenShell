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
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    import bpy
    import ifcopenshell
    import bonsai.tool as tool


def copy_attribute_to_selection(
    ifc: tool.Ifc, root: tool.Root, name: str, value: Union[str, None], obj: bpy.types.Object
) -> bool:
    if element := ifc.get_entity(obj):
        try:
            ifc.run("attribute.edit_attributes", product=element, attributes={name: value})
            if name in ("Name", "AxisTag"):
                root.set_object_name(obj, element)
            return True
        except:
            pass
    return False
