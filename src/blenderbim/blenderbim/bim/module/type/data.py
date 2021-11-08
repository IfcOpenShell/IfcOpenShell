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
import blenderbim.tool as tool


def refresh():
    TypeData.is_loaded = False


class TypeData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "relating_type_classes": cls.relating_type_classes(),
            "relating_types": cls.relating_types(),
        }
        cls.is_loaded = True

    @classmethod
    def relating_type_classes(cls):
        results = []
        element = tool.Ifc.get_entity(bpy.context.active_object)
        types = ifcopenshell.util.type.get_applicable_types(element.is_a(), schema=tool.Ifc.get_schema())
        applicable_types_enum.extend((t, t, "") for t in types)
        return results

    @classmethod
    def relating_types(cls):
        results = []
        elements = tool.Ifc.get().by_type(bpy.context.active_object.BIMTypeProperties.relating_type_class)
        elements = [(str(e.id()), e.Name, "") for e in elements]
        relating_types_enum.extend(sorted(elements, key=lambda s: s[1]))
        return results
