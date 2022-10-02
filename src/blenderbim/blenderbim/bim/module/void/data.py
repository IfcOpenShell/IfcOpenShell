# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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
import blenderbim.tool as tool


def refresh():
    BooleansData.is_loaded = False


class BooleansData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"total_booleans": cls.total_booleans()}
        cls.is_loaded = True

    @classmethod
    def total_booleans(cls):
        obj = bpy.context.active_object
        if (
            not obj.data
            or not hasattr(obj.data, "BIMMeshProperties")
            or not obj.data.BIMMeshProperties.ifc_definition_id
        ):
            return 0
        representation = tool.Ifc.get().by_id(obj.data.BIMMeshProperties.ifc_definition_id)
        total_booleans = 0
        for item in representation.Items:
            while True:
                if item.is_a("IfcBooleanResult"):
                    total_booleans += 1
                    item = item.FirstOperand
                else:
                    break
        return total_booleans
