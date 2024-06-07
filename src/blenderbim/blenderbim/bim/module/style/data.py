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
import ifcopenshell
import blenderbim.tool as tool
from ifcopenshell.util.doc import get_entity_doc


def refresh():
    StylesData.is_loaded = False


class StylesData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "styles_to_blender_material_names": cls.styles_to_blender_material_names(),
            "style_types": cls.style_types(),
            "total_styles": cls.total_styles(),
            "reflectance_methods": cls.reflectance_methods(),
        }
        cls.is_loaded = True

    @classmethod
    def styles_to_blender_material_names(cls):
        ifc_file = tool.Ifc.get()
        props = bpy.context.scene.BIMStylesProperties
        materials = []
        for style in props.styles:
            material = tool.Ifc.get_object(ifc_file.by_id(style.ifc_definition_id))
            materials.append(material.name if material is not None else None)
        return materials

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
    def total_styles(cls):
        return len(tool.Ifc.get().by_type("IfcPresentationStyle"))
