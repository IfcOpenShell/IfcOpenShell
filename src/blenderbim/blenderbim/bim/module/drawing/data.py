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
import ifcopenshell.util.representation
import blenderbim.tool as tool


def refresh():
    TextData.is_loaded = False


class TextData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"attributes": cls.attributes()}
        cls.is_loaded = True

    @classmethod
    def attributes(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if not element or not element.is_a("IfcAnnotation") or element.ObjectType not in ["TEXT", "TEXT_LEADER"]:
            return []
        rep = ifcopenshell.util.representation.get_representation(element, "Plan", "Annotation")
        text_literal = [i for i in rep.Items if i.is_a("IfcTextLiteral")][0]
        return [
            {"name": "Literal", "value": text_literal.Literal},
            {"name": "BoxAlignment", "value": text_literal.BoxAlignment},
        ]
