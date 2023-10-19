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
    StyleAttributesData.is_loaded = False


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
    def total_styles(cls):
        return len(tool.Ifc.get().by_type("IfcPresentationStyle"))


class StyleAttributesData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "ifc_style_id": cls.ifc_style_id(),
            "attributes": cls.get_attributes(),
            "style_elements": cls.get_style_elements(),
        }
        cls.data["external_style_attributes"] = cls.get_external_style_attributes()
        cls.is_loaded = True

    @classmethod
    def ifc_style_id(cls):
        return bpy.context.active_object.active_material.BIMMaterialProperties.ifc_style_id

    @classmethod
    def get_attributes(cls):
        style = tool.Ifc.get().by_id(bpy.context.active_object.active_material.BIMMaterialProperties.ifc_style_id)
        results = []
        for name, value in style.get_info().items():
            if name in ["id", "type", "Styles"]:
                continue
            results.append({"name": name, "value": str(value)})
        return results

    @classmethod
    def get_style_elements(cls):
        return tool.Style.get_style_elements(bpy.context.active_object.active_material)

    @classmethod
    def get_external_style_attributes(cls):
        external_style = cls.data["style_elements"].get("IfcExternallyDefinedSurfaceStyle", None)
        if not external_style:
            return None
        results = []
        for name, value in external_style.get_info().items():
            if name in ["id", "type"]:
                continue
            results.append({"name": name, "value": str(value)})
        return results
