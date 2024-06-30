# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import blenderbim.core.tool as tool
from typing import Literal


def join_wall_LV(blender: tool.Blender, joiner, join_type: Literal["L", "V"] = "L") -> None:
    if len(selected_objs := blender.get_selected_objects()) != 2:
        raise RequireTwoObjectsError()

    active_obj = blender.get_active_object()
    another_selected_object = next(o for o in selected_objs if o != active_obj)
    if join_type == "L":
        joiner.join_L(another_selected_object, active_obj)
    elif join_type == "V":
        joiner.join_V(another_selected_object, active_obj)


class RequireTwoObjectsError(Exception):
    pass
