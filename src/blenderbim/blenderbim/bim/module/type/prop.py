# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
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
from blenderbim.bim.prop import StrProperty, Attribute
from blenderbim.bim.ifc import IfcStore
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

applicable_types_enum = []
relating_types_enum = []
type_classes_enum = []
available_types_enum = []


def purge():
    global applicable_types_enum
    global relating_types_enum
    global type_classes_enum
    global available_types_enum
    applicable_types_enum = []
    relating_types_enum = []
    type_classes_enum = []
    available_types_enum = []


def getIfcTypes(self, context):
    global type_classes_enum
    file = IfcStore.get_file()
    if len(type_classes_enum) < 1 and file:
        classes = set([e.is_a() for e in file.by_type("IfcElementType")])
        type_classes_enum.extend([(c, c, "") for c in sorted(classes)])
    return type_classes_enum


def get_relating_type(self, context):
    global available_types_enum
    if len(available_types_enum) < 1 and getIfcTypes(self, context):
        elements = [(str(e.id()), e.Name, "") for e in IfcStore.get_file().by_type(self.ifc_class)]
        available_types_enum.extend(sorted(elements, key=lambda s: s[1]))
    return available_types_enum


def updateTypeInstanceIfcClass(self, context):
    global type_classes_enum
    global available_types_enum
    type_classes_enum.clear()
    available_types_enum.clear()


def getApplicableTypes(self, context):
    global applicable_types_enum
    if len(applicable_types_enum) < 1:
        element = IfcStore.get_file().by_id(context.active_object.BIMObjectProperties.ifc_definition_id)
        types = ifcopenshell.util.type.get_applicable_types(element.is_a(), schema=IfcStore.get_file().schema)
        applicable_types_enum.extend((t, t, "") for t in types)
    return applicable_types_enum


def get_object_relating_type(self, context):
    global relating_types_enum
    if len(relating_types_enum) < 1:
        elements = IfcStore.get_file().by_type(context.active_object.BIMTypeProperties.relating_type_class)
        elements = [(str(e.id()), e.Name, "") for e in elements]
        relating_types_enum.extend(sorted(elements, key=lambda s: s[1]))
    return relating_types_enum


def updateTypeDropdowns(self, context):
    global applicable_types_enum
    global relating_types_enum
    applicable_types_enum.clear()
    relating_types_enum.clear()


class BIMTypeProperties(PropertyGroup):
    ifc_class: bpy.props.EnumProperty(items=getIfcTypes, name="IFC Class", update=updateTypeInstanceIfcClass)
    relating_type: bpy.props.EnumProperty(items=get_relating_type, name="Relating Type")


class BIMTypeObjectProperties(PropertyGroup):
    is_editing_type: BoolProperty(name="Is Editing Type", update=updateTypeDropdowns)
    relating_type_class: EnumProperty(items=getApplicableTypes, name="Relating Type Class")
    relating_type: EnumProperty(items=get_object_relating_type, name="Relating Type")
