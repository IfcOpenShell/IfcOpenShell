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
import ifcopenshell.util.representation


class Drawing(blenderbim.core.tool.Drawing):
    @classmethod
    def disable_editing_text(cls, obj):
        obj.BIMTextProperties.is_editing = False

    @classmethod
    def disable_editing_text_product(cls, obj):
        obj.BIMTextProperties.is_editing_product = False

    @classmethod
    def enable_editing_text(cls, obj):
        obj.BIMTextProperties.is_editing = True

    @classmethod
    def enable_editing_text_product(cls, obj):
        obj.BIMTextProperties.is_editing_product = True

    @classmethod
    def export_text_literal_attributes(cls, obj):
        return blenderbim.bim.helper.export_attributes(obj.BIMTextProperties.attributes)

    @classmethod
    def get_text_literal(cls, obj):
        element = tool.Ifc.get_entity(obj)
        if not element:
            return
        rep = ifcopenshell.util.representation.get_representation(element, "Plan", "Annotation")
        if not rep:
            return
        items = [i for i in rep.Items if i.is_a("IfcTextLiteral")]
        if items:
            return items[0]

    @classmethod
    def get_text_product(cls, element):
        for rel in element.HasAssignments:
            if rel.is_a("IfcRelAssignsToProduct"):
                return rel.RelatingProduct

    @classmethod
    def import_text_attributes(cls, obj):
        props = obj.BIMTextProperties
        props.attributes.clear()
        text = cls.get_text_literal(obj)
        blenderbim.bim.helper.import_attributes2(text, props.attributes)

    @classmethod
    def import_text_product(cls, obj):
        element = tool.Ifc.get_entity(obj)
        product = cls.get_text_product(element)
        if product:
            obj.BIMTextProperties.relating_product = tool.Ifc.get_object(product)
        else:
            obj.BIMTextProperties.relating_product = None

    @classmethod
    def update_text_value(cls, obj):
        element = cls.get_text_literal(obj)
        if element:
            obj.BIMTextProperties.value = element.Literal
