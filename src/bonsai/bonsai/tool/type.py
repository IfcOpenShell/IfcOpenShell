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
import ifcopenshell.util.element
import ifcopenshell.util.representation
import bonsai.core.tool
import bonsai.core.geometry
import bonsai.tool as tool
import bonsai.bim.helper
from typing import Union


class Type(bonsai.core.tool.Type):
    @classmethod
    def change_object_data(cls, obj: bpy.types.Object, data: bpy.types.ID, is_global: bool = False) -> None:
        tool.Geometry.change_object_data(obj, data, is_global)

    @classmethod
    def disable_editing(cls, obj: bpy.types.Object) -> None:
        obj.BIMTypeProperties.is_editing_type = False

    @classmethod
    def get_body_context(cls) -> ifcopenshell.entity_instance:
        return ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body", "MODEL_VIEW")

    @classmethod
    def get_body_representation(
        cls, element: ifcopenshell.entity_instance
    ) -> Union[ifcopenshell.entity_instance, None]:
        if element.is_a("IfcProduct") and element.Representation and element.Representation.Representations:
            for representation in element.Representation.Representations:
                if representation.ContextOfItems.ContextIdentifier == "Body":
                    return representation
        elif element.is_a("IfcTypeProduct") and element.RepresentationMaps:
            for representation_map in element.RepresentationMaps:
                if representation_map.MappedRepresentation.ContextOfItems.ContextIdentifier == "Body":
                    return representation_map.MappedRepresentation

    @classmethod
    def get_ifc_representation_class(cls, element: ifcopenshell.entity_instance) -> Union[str, None]:
        material = ifcopenshell.util.element.get_material(element)
        if material:
            if material.is_a("IfcMaterialProfileSetUsage"):
                return "IfcExtrudedAreaSolid/IfcMaterialProfileSetUsage"
            elif material.is_a("IfcMaterialLayerSetUsage"):
                return "IfcExtrudedAreaSolid/IfcArbitraryProfileDefWithVoids"

    @classmethod
    def get_model_types(cls) -> list[ifcopenshell.entity_instance]:
        ifc_file = tool.Ifc.get()
        types = ifc_file.by_type("IfcElementType")
        # exclude IfcSpatialElementType
        types += ifc_file.by_type("IfcTypeProduct", include_subtypes=False)
        if not tool.Ifc.get_schema().startswith("IFC4X3"):
            types += ifc_file.by_type("IfcWindowStyle")
            types += ifc_file.by_type("IfcDoorStyle")
        return types

    @classmethod
    def get_object_data(cls, obj: bpy.types.Object) -> Union[bpy.types.ID, None]:
        return obj.data

    @classmethod
    def get_profile_set_usage(cls, element: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        material = ifcopenshell.util.element.get_material(element)
        if material:
            if material.is_a("IfcMaterialProfileSetUsage"):
                return material

    @classmethod
    def get_representation_context(cls, representation: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
        return representation.ContextOfItems

    @classmethod
    def get_type_occurrences(cls, element_type: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        return ifcopenshell.util.element.get_types(element_type)

    @classmethod
    def has_material_usage(cls, element: ifcopenshell.entity_instance) -> bool:
        material = ifcopenshell.util.element.get_material(element)
        if material:
            return "Usage" in material.is_a()
        return False

    @classmethod
    def run_geometry_add_representation(
        cls,
        obj: bpy.types.Object,
        context: ifcopenshell.entity_instance,
        ifc_representation_class: Union[str, None] = None,
        profile_set_usage: Union[ifcopenshell.entity_instance, None] = None,
    ) -> ifcopenshell.entity_instance:
        return bonsai.core.geometry.add_representation(
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
        cls,
        obj: bpy.types.Object,
        representation: ifcopenshell.entity_instance,
        should_reload: bool = False,
        is_global: bool = False,
    ) -> None:
        return bonsai.core.geometry.switch_representation(
            tool.Ifc,
            tool.Geometry,
            obj=obj,
            representation=representation,
            should_reload=should_reload,
            is_global=is_global,
            should_sync_changes_first=False,
        )
