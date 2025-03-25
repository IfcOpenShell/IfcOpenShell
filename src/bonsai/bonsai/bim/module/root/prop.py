# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.util.schema
import ifcopenshell.util.type
import bonsai.tool as tool
from bonsai.bim.module.root.data import IfcClassData
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    CollectionProperty,
)
from typing import TYPE_CHECKING, Union


def get_ifc_predefined_types(self: "BIMRootProperties", context: bpy.types.Context) -> list[tuple[str, str]]:
    if not IfcClassData.is_loaded:
        IfcClassData.load()
    return IfcClassData.data["ifc_predefined_types"]


def get_representation_template(self: "BIMRootProperties", context: bpy.types.Context) -> list[tuple[str, str]]:
    if not IfcClassData.is_loaded:
        IfcClassData.load()
    return IfcClassData.data["representation_template"]


def refresh_classes(self: "BIMRootProperties", context: bpy.types.Context) -> None:
    old_class = self.ifc_class
    old_predefined_type = self.ifc_predefined_type if get_ifc_predefined_types(self, context) else ""

    enum = get_ifc_classes(self, context)
    self.ifc_class = enum[0][0]
    IfcClassData.load()

    if self.ifc_product == "IfcFeatureElement":
        if (obj := tool.Blender.get_active_object(is_selected=True)) and obj.type == "MESH":
            self.featured_obj = obj
            self.representation_template = "EXTRUSION"
            self.representation_obj = None
    elif (obj := tool.Blender.get_active_object(is_selected=True)) and obj.type == "MESH":
        self.representation_template = "OBJ"
        self.representation_obj = obj

    ifc_file = tool.Ifc.get()
    # When switching between ElementType and Element, keep the same class and predefined type if possible
    if self.ifc_product == "IfcElement":
        ifc_class = next(iter(ifcopenshell.util.type.get_applicable_entities(old_class, ifc_file.schema)), None)
    elif self.ifc_product == "IfcElementType":
        ifc_class = next(iter(ifcopenshell.util.type.get_applicable_types(old_class, ifc_file.schema)), None)
    else:
        return
    if ifc_class:
        self.ifc_class = ifc_class
        if old_predefined_type:
            self.ifc_predefined_type = old_predefined_type


def refresh_predefined_types(self: "BIMRootProperties", context: bpy.types.Context) -> None:
    IfcClassData.load()
    enum = get_ifc_predefined_types(self, context)
    if enum:
        self.ifc_predefined_type = enum[0][0]


def get_ifc_products(self: "BIMRootProperties", context: bpy.types.Context) -> list[tuple[str, str]]:
    if not IfcClassData.is_loaded:
        IfcClassData.load()
    return IfcClassData.data["ifc_products"]


def get_ifc_classes(self: "BIMRootProperties", context: bpy.types.Context) -> list[tuple[str, str]]:
    if not IfcClassData.is_loaded:
        IfcClassData.load()
    return IfcClassData.data["ifc_classes"]


def get_ifc_classes_suggestions() -> dict[str, list[dict[str, Union[str, None]]]]:
    if not IfcClassData.is_loaded:
        IfcClassData.load()
    return IfcClassData.data["ifc_classes_suggestions"]


def get_contexts(self: "BIMRootProperties", context: bpy.types.Context) -> list[tuple[str, str]]:
    if not IfcClassData.is_loaded:
        IfcClassData.load()
    return IfcClassData.data["contexts"]


def get_profile(self: "BIMRootProperties", context: bpy.types.Context) -> list[tuple[str, str]]:
    if not IfcClassData.is_loaded:
        IfcClassData.load()
    return IfcClassData.data["profile"]


def update_relating_class_from_object(self: "BIMRootProperties", context: bpy.types.Context) -> None:
    if self.relating_class_object is None:
        return
    element = tool.Ifc.get_entity(self.relating_class_object)
    if not element:
        return
    self.ifc_class = element.is_a()
    predefined_type = ifcopenshell.util.element.get_predefined_type(element)
    if predefined_type:
        if element.PredefinedType == "USERDEFINED":
            self.ifc_predefined_type = "USERDEFINED"
            self.ifc_userdefined_type = predefined_type
        else:
            self.ifc_predefined_type = predefined_type
    bpy.ops.bim.reassign_class()


def is_object_class_applicable(self: "BIMRootProperties", obj: bpy.types.Object) -> bool:
    element = tool.Ifc.get_entity(obj)
    if not element:
        return False
    active_element = tool.Ifc.get_entity(bpy.context.active_object)
    if not active_element:
        return False
    return element.is_a("IfcTypeObject") == active_element.is_a("IfcTypeObject")


def poll_representation_obj(self: "BIMRootProperties", obj: bpy.types.Object) -> bool:
    return obj.type == "MESH" and obj.data.polygons


def poll_featured_obj(self: "BIMRootProperties", obj: bpy.types.Object) -> bool:
    return tool.Ifc.get_entity(obj)


class BIMRootProperties(PropertyGroup):
    contexts: EnumProperty(items=get_contexts, name="Contexts", options=set())
    name: StringProperty(name="Name")
    description: StringProperty(name="Description")
    ifc_product: EnumProperty(items=get_ifc_products, name="Products", update=refresh_classes)
    ifc_class: EnumProperty(items=get_ifc_classes, name="Class", update=refresh_predefined_types)
    ifc_predefined_type: EnumProperty(items=get_ifc_predefined_types, name="Predefined Type", default=None)
    ifc_userdefined_type: StringProperty(name="Userdefined Type")
    featured_obj: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Featured Object",
        poll=poll_featured_obj,
        description="The feature will be applied to this object",
    )
    representation_template: bpy.props.EnumProperty(
        items=get_representation_template, name="Representation Template", default=0
    )
    representation_obj: bpy.props.PointerProperty(
        type=bpy.types.Object,
        name="Representation Object",
        poll=poll_representation_obj,
        description="The representation will be a tessellation of the selected object",
    )
    profile: EnumProperty(name="Profile for profile type object", items=get_profile)
    relating_class_object: PointerProperty(
        type=bpy.types.Object,
        name="Copy Class",
        update=update_relating_class_from_object,
        poll=is_object_class_applicable,
        description="Copy the selected object's class and predefined type to the active object",
    )

    getter_enum_suggestions = {
        "ifc_class": get_ifc_classes_suggestions,
    }

    if TYPE_CHECKING:
        contexts: str
        description: str
        ifc_product: str
        ifc_class: str
        ifc_predefined_type: str
        ifc_userdefined_type: str
        featured_obj: Union[bpy.types.Object, None]
        representation_template: str
        representation_obj: Union[bpy.types.Object, None]
        profile: str
        relating_class_object: Union[bpy.types.Object, None]
