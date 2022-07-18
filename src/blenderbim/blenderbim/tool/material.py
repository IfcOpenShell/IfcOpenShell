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
import blenderbim.core.tool
import blenderbim.tool as tool
import blenderbim.bim.helper


class Material(blenderbim.core.tool.Material):
    @classmethod
    def add_default_material_object(cls):
        return bpy.data.materials.new("Default")

    @classmethod
    def delete_object(cls, obj):
        bpy.data.materials.remove(obj)

    @classmethod
    def disable_editing_materials(cls):
        bpy.context.scene.BIMMaterialProperties.is_editing = False

    @classmethod
    def enable_editing_materials(cls):
        bpy.context.scene.BIMMaterialProperties.is_editing = True

    @classmethod
    def get_active_material_type(cls):
        return bpy.context.scene.BIMMaterialProperties.material_type

    @classmethod
    def get_elements_by_material(cls, material):
        return ifcopenshell.util.element.get_elements_by_material(tool.Ifc.get(), material)

    @classmethod
    def get_name(cls, obj):
        return obj.name

    @classmethod
    def import_material_definitions(cls, material_type):
        props = bpy.context.scene.BIMMaterialProperties
        expanded_categories = {m.name for m in props.materials if m.is_expanded}
        props.materials.clear()
        get_name = lambda x: x.Name or "Unnamed"
        if material_type == "IfcMaterialLayerSet":
            get_name = lambda x: x.LayerSetName or "Unnamed"
        elif material_type == "IfcMaterialList":
            get_name = lambda x: "Unnamed"
        materials = sorted(tool.Ifc.get().by_type(material_type), key=get_name)
        categories = {}
        if material_type == "IfcMaterial":
            [categories.setdefault(getattr(m, "Category", "Uncategorised"), []).append(m) for m in materials]
            for category, mats in categories.items():
                cat = props.materials.add()
                cat.name = category or ""
                cat.is_category = True
                cat.is_expanded = cat.name in expanded_categories
                for material in mats if cat.is_expanded else []:
                    new = props.materials.add()
                    new.ifc_definition_id = material.id()
                    new.name = get_name(material)
                    new.total_elements = len(
                        ifcopenshell.util.element.get_elements_by_material(tool.Ifc.get(), material)
                    )
            return
        for material in materials:
            new = props.materials.add()
            new.ifc_definition_id = material.id()
            new.name = get_name(material)
            new.total_elements = len(ifcopenshell.util.element.get_elements_by_material(tool.Ifc.get(), material))

    @classmethod
    def is_editing_materials(cls):
        return bpy.context.scene.BIMMaterialProperties.is_editing

    @classmethod
    def select_elements(cls, elements):
        for element in elements:
            obj = tool.Ifc.get_object(element)
            if obj:
                obj.select_set(True)
