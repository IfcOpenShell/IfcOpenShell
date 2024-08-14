# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bonsai.core.tool
import bonsai.tool as tool
import ifcopenshell.util.element


class Nest(bonsai.core.tool.Nest):
    @classmethod
    def can_nest(cls, relating_obj, related_obj):
        relating_object = tool.Ifc.get_entity(relating_obj)
        related_object = tool.Ifc.get_entity(related_obj)
        if not relating_object or not related_object:
            return False
        if relating_object.is_a("IfcElement") and related_object.is_a("IfcElement"):
            return True
        return False

    @classmethod
    def disable_editing(cls, obj):
        obj.BIMObjectNestProperties.is_editing = False

    @classmethod
    def enable_editing(cls, obj):
        obj.BIMObjectNestProperties.is_editing = True

    @classmethod
    def get_container(cls, element):
        return ifcopenshell.util.element.get_container(element)

    @classmethod
    def get_relating_object(cls, related_element):
        return ifcopenshell.util.element.get_nest(related_element)
