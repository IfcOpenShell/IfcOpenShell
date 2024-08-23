# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

import bpy
import ifcopenshell.util.type
import ifcopenshell.util.element
from ifcopenshell.util.doc import get_entity_doc
import bonsai.tool as tool


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
                "relating_type": cls.relating_type(),
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
        version = tool.Ifc.get_schema()
        types = ifcopenshell.util.type.get_applicable_types(element.is_a(), schema=version)
        if element.is_a("IfcAnnotation"):
            types.append("IfcTypeProduct")
        results.extend((t, t, get_entity_doc(version, t).get("description", "")) for t in types)
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
    def relating_type(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        element_type = ifcopenshell.util.element.get_type(element)
        if element_type:
            return {"id": element_type.id(), "name": f"{element_type.is_a()}/{element_type.Name or 'Unnamed'}"}
