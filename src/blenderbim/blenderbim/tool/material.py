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

import ifcopenshell
import blenderbim.core.tool
import blenderbim.tool as tool
import blenderbim.bim.helper


class Material(blenderbim.core.tool.Material):
    @classmethod
    def link(cls, material, obj):
        obj.BIMObjectProperties.ifc_definition_id = material.id()

    @classmethod
    def unlink(self, obj):
        obj.BIMObjectProperties.ifc_definition_id = 0
