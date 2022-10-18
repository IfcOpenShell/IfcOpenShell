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
import ifcopenshell.util.type
import ifcopenshell.util.element
import blenderbim.tool as tool


def refresh():
    TypeData.is_loaded = False


class TypeData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        # These two are loaded discretely because relating_types depends on relating_type_classes
        cls.data["relating_type_classes"] = cls.relating_type_classes()
        cls.data["relating_types"] = cls.relating_types()
        cls.data.update(
            {
                "is_product": cls.is_product(),
                "total_instances": cls.total_instances(),
                "type_name": cls.type_name(),
            }
        )

    @classmethod
    def relating_type_classes(cls):
        results = []
        obj = bpy.context.active_object
        if not obj:
            return
        element = tool.Ifc.get_entity(obj)
        if not element:
            return []
        types = ifcopenshell.util.type.get_applicable_types(element.is_a(), schema=tool.Ifc.get_schema())
        results.extend((t, t, "") for t in types)
        return results

    @classmethod
    def relating_types(cls):
        relating_type_classes = cls.relating_type_classes()
        if not relating_type_classes:
            return []
        results = []
        relating_type_class = bpy.context.active_object.BIMTypeProperties.relating_type_class
        if not relating_type_class and relating_type_classes:
            relating_type_class = relating_type_classes[0][0]
        elements = tool.Ifc.get().by_type(relating_type_class)
        elements = [(str(e.id()), e.Name or "Unnamed", "") for e in elements]
        results.extend(sorted(elements, key=lambda s: s[1]))
        return results

    @classmethod
    def is_product(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        return element.is_a("IfcProduct")

    @classmethod
    def total_instances(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        return str(len(ifcopenshell.util.element.get_types(element)))

    @classmethod
    def type_name(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        type = ifcopenshell.util.element.get_type(element)
        if type:
            return f"{type.is_a()}/{type.Name or 'Unnamed'}"
