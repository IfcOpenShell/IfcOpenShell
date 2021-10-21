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

import bpy
import blenderbim.core.tool
import blenderbim.tool as tool
from mathutils import Vector


class Qto(blenderbim.core.tool.Qto):
    @classmethod
    def get_radius_of_selected_vertices(cls, obj):
        selected_verts = [v.co for v in obj.data.vertices if v.select]
        total = Vector()
        for v in selected_verts:
            total += v
        circle_center = total / len(selected_verts)
        return max([(v - circle_center).length for v in selected_verts])

    @classmethod
    def set_qto_result(cls, result):
        bpy.context.scene.BIMQtoProperties.qto_result = str(round(result, 3))
