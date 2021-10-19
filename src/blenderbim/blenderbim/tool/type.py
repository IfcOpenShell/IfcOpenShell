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


class Type(blenderbim.core.tool.Type):
    @classmethod
    def disable_editing(cls, obj):
        obj.BIMTypeProperties.is_editing_type = False

    @classmethod
    def get_any_representation(cls, element):
        if element.is_a("IfcProduct") and element.Representation and element.Representation.Representations:
            return element.Representation.Representations[0]
        elif element.is_a("IfcTypeProduct") and element.RepresentationMaps:
            return element.RepresentationMaps[0].MappedRepresentation

    @classmethod
    def get_body_representation(cls, element):
        if element.is_a("IfcProduct") and element.Representation and element.Representation.Representations:
            for representation in element.Representation.Representations:
                if representation.ContextOfItems.ContextIdentifier == "Body":
                    return representation
        elif element.is_a("IfcTypeProduct") and element.RepresentationMaps:
            for representation_map in element.RepresentationMaps:
                if representation_map.MappedRepresentation.ContextOfItems.ContextIdentifier == "Body":
                    return representation_map.MappedRepresentation

    @classmethod
    def has_dynamic_voids(cls, obj):
        for modifier in obj.modifiers:
            if modifier.name == "IfcOpeningElement" and modifier.type == "BOOLEAN":
                return True
        return False
