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


class Owner(blenderbim.core.tool.Owner):
    @classmethod
    def set_user(cls, user):
        bpy.context.scene.BIMOwnerProperties.active_user_id = user.id()

    @classmethod
    def get_user(cls):
        if bpy.context.scene.BIMOwnerProperties.active_user_id:
            return tool.Ifc.get().by_id(bpy.context.scene.BIMOwnerProperties.active_user_id)

    @classmethod
    def clear_user(cls):
        bpy.context.scene.BIMOwnerProperties.active_user_id = 0
