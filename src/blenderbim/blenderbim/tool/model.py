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
import blenderbim.core.tool
import blenderbim.tool as tool


class Model(blenderbim.core.tool.Model):
    @classmethod
    def generate_occurrence_name(cls, element_type, ifc_class):
        props = bpy.context.scene.BIMModelProperties
        if props.occurrence_name_style == "CLASS":
            return ifc_class[3:]
        elif props.occurrence_name_style == "TYPE":
            return element_type.Name or "Unnamed"
        elif props.occurrence_name_style == "CUSTOM":
            try:
                # Power users gonna power
                return eval(props.occurrence_name_function) or "Instance"
            except:
                return "Instance"

    @classmethod
    def get_extrusion(cls, representation):
        item = representation.Items[0]
        while True:
            if item.is_a("IfcExtrudedAreaSolid"):
                return item
            elif item.is_a("IfcBooleanResult"):
                item = item.FirstOperand
            else:
                break
