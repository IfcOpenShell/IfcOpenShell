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


def get_ifc_predefined_types(self, context):
    if not IfcClassData.is_loaded:
        IfcClassData.load()
    return IfcClassData.data["ifc_predefined_types"]


def get_representation_template(self, context):
    if not IfcClassData.is_loaded:
        IfcClassData.load()
    return IfcClassData.data["representation_template"]


def refresh_classes(self, context):
    enum = get_ifc_classes(self, context)
    context.scene.BIMRootProperties.ifc_class = enum[0][0]
    IfcClassData.load()


def refresh_predefined_types(self, context):
    IfcClassData.load()
    enum = get_ifc_predefined_types(self, context)
    if enum:
        context.scene.BIMRootProperties.ifc_predefined_type = enum[0][0]


def update_class_enum(self, context):
    self.ifc_class = self.ifc_class_filter_enum


def get_ifc_products(self, context):
    if not IfcClassData.is_loaded:
        IfcClassData.load()
    return IfcClassData.data["ifc_products"]


def get_ifc_classes(self, context):
    if not IfcClassData.is_loaded:
        IfcClassData.load()
    return IfcClassData.data["ifc_classes"]


def get_ifc_classes_suggestions():
    if not IfcClassData.is_loaded:
        IfcClassData.load()
    return IfcClassData.data["ifc_classes_suggestions"]


def get_contexts(self, context):
    if not IfcClassData.is_loaded:
        IfcClassData.load()
    return IfcClassData.data["contexts"]


def get_profile(self, context):
    if not IfcClassData.is_loaded:
        IfcClassData.load()
    return IfcClassData.data["profile"]


def update_relating_class_from_object(self, context):
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


def is_object_class_applicable(self, obj):
    element = tool.Ifc.get_entity(obj)
    if not element:
        return False
    active_element = tool.Ifc.get_entity(bpy.context.active_object)
    if not active_element:
        return False
    return element.is_a("IfcTypeObject") == active_element.is_a("IfcTypeObject")


def poll_representation_obj(self, obj):
    return obj.type == "MESH" and obj.data.polygons


class BIMRootProperties(PropertyGroup):
    contexts: EnumProperty(items=get_contexts, name="Contexts", options=set())
    ifc_product: EnumProperty(items=get_ifc_products, name="Products", update=refresh_classes)
    ifc_class: EnumProperty(items=get_ifc_classes, name="Class", update=refresh_predefined_types)
    ifc_predefined_type: EnumProperty(items=get_ifc_predefined_types, name="Predefined Type", default=None)
    ifc_userdefined_type: StringProperty(name="Userdefined Type")
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
