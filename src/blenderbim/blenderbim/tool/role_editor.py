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
import blenderbim.bim.helper


class RoleEditor(blenderbim.core.tool.RoleEditor):
    @classmethod
    def set_role(cls, role):
        bpy.context.scene.BIMOwnerProperties.active_role_id = role.id()

    @classmethod
    def import_attributes(cls):
        role = cls.get_role()
        props = bpy.context.scene.BIMOwnerProperties
        props.role_attributes.clear()
        blenderbim.bim.helper.import_attributes("IfcActorRole", props.role_attributes, role.get_info())

    @classmethod
    def clear_role(cls):
        bpy.context.scene.BIMOwnerProperties.active_role_id = 0

    @classmethod
    def get_role(cls):
        return tool.Ifc().get().by_id(bpy.context.scene.BIMOwnerProperties.active_role_id)

    @classmethod
    def export_attributes(cls):
        return blenderbim.bim.helper.export_attributes(bpy.context.scene.BIMOwnerProperties.role_attributes)
