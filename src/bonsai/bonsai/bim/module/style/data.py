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
import ifcopenshell
import ifcopenshell.util.schema
import bonsai.tool as tool
from ifcopenshell.util.doc import get_entity_doc
from typing import Union


def refresh():
    StylesData.is_loaded = False
    BlenderMaterialStyleData.is_loaded = False


class StylesData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "style_types": cls.style_types(),
            "total_styles": cls.total_styles(),
            "reflectance_methods": cls.reflectance_methods(),
        }
        cls.is_loaded = True

    @classmethod
    def reflectance_methods(cls):
        declaration = tool.Ifc.schema().declaration_by_name("IfcReflectanceMethodEnum")
        return [(i, i, "") for i in declaration.enumeration_items()]

    @classmethod
    def style_types(cls):
        declaration = tool.Ifc.schema().declaration_by_name("IfcPresentationStyle")
        declarations = ifcopenshell.util.schema.get_subtypes(declaration)
        version = tool.Ifc.get_schema()
        return [
            (c, c, get_entity_doc(version, c).get("description", "")) for c in sorted([d.name() for d in declarations])
        ]

    @classmethod
    def total_styles(cls) -> dict[str, int]:
        total: dict[str, int] = {}
        ifc_file = tool.Ifc.get()
        for decl in cls.get_presentation_style_declarations():
            total[decl.name()] = len(ifc_file.by_type(decl.name()))
        return total

    @classmethod
    def get_presentation_style_declarations(cls):
        declaration = tool.Ifc.schema().declaration_by_name("IfcPresentationStyle")
        return ifcopenshell.util.schema.get_subtypes(declaration)


class BlenderMaterialStyleData:
    style: Union[ifcopenshell.entity_instance, None] = None
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "is_linked_to_style": cls.is_linked_to_style(),
            # After is_linked_to_style.
            "linked_style_name": cls.linked_style_name(),
        }
        cls.is_loaded = True

    @classmethod
    def is_linked_to_style(cls) -> bool:
        ifc_file = tool.Ifc.get()
        if not ifc_file:
            return False
        context = bpy.context
        cls.linked_style = None
        obj = context.active_object
        if not obj:
            return False
        material = obj.active_material
        if not material:
            return False
        props = material.BIMStyleProperties
        style_id = props.ifc_definition_id
        style = tool.Ifc.get_entity_by_id(style_id)
        if not style:
            return False

        # Double check that it's the right material
        # and not material from other Blender session.
        linked_material = tool.Ifc.get_object(style)
        if linked_material != material:
            return False
        cls.style = style
        return True

    @classmethod
    def linked_style_name(cls) -> Union[str, None]:
        """Return str if Blender Material is linked to IFC style or None if it's not.

        Method will return "Unnamed" if style name is None.
        """
        if cls.style:
            return cls.style.Name or "Unnamed"
        return None
