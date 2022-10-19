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
import blenderbim.core.geometry
import blenderbim.tool as tool
import blenderbim.bim.helper


class Type(blenderbim.core.tool.Type):
    @classmethod
    def change_object_data(cls, obj, data, is_global=False):
        if is_global:
            obj.data.user_remap(data)
        else:
            obj.data = data

    @classmethod
    def disable_editing(cls, obj):
        obj.BIMTypeProperties.is_editing_type = False

    @classmethod
    def get_body_context(cls):
        return ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")

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
    def get_ifc_representation_class(cls, element):
        material = ifcopenshell.util.element.get_material(element)
        if material:
            if material.is_a("IfcMaterialProfileSetUsage"):
                return "IfcExtrudedAreaSolid/IfcMaterialProfileSetUsage"
            elif material.is_a("IfcMaterialLayerSetUsage"):
                return "IfcExtrudedAreaSolid/IfcArbitraryProfileDefWithVoids"

    @classmethod
    def get_object_data(cls, obj):
        return obj.data

    @classmethod
    def get_profile_set_usage(cls, element):
        material = ifcopenshell.util.element.get_material(element)
        if material:
            if material.is_a("IfcMaterialProfileSetUsage"):
                return material

    @classmethod
    def get_representation_context(cls, representation):
        return representation.ContextOfItems

    @classmethod
    def has_material_usage(cls, element):
        material = ifcopenshell.util.element.get_material(element)
        if material:
            return "Usage" in material.is_a()
        return False

    @classmethod
    def run_geometry_add_representation(
        cls, obj=None, context=None, ifc_representation_class=None, profile_set_usage=None
    ):
        return blenderbim.core.geometry.add_representation(
            tool.Ifc,
            tool.Geometry,
            tool.Style,
            tool.Surveyor,
            obj=obj,
            context=context,
            ifc_representation_class=ifc_representation_class,
            profile_set_usage=profile_set_usage,
        )

    @classmethod
    def run_geometry_switch_representation(
        cls, obj=None, representation=None, should_reload=None, is_global=None
    ):
        return blenderbim.core.geometry.switch_representation(
            tool.Geometry,
            obj=obj,
            representation=representation,
            should_reload=should_reload,
            is_global=is_global,
            should_sync_changes_first=False,
        )
