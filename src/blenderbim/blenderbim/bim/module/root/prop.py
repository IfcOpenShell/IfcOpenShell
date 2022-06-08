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
import ifcopenshell
import ifcopenshell.util.schema
from blenderbim.bim.module.root.data import IfcClassData
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

types_enum = []


def purge():
    global types_enum
    types_enum = []


def getIfcPredefinedTypes(self, context):
    global types_enum
    file = IfcStore.get_file()
    if len(types_enum) < 1 and file:
        declaration = IfcStore.get_schema().declaration_by_name(self.ifc_class)
        for attribute in declaration.attributes():
            if attribute.name() == "PredefinedType":
                types_enum.extend(
                    [(e, e, "") for e in attribute.type_of_attribute().declared_type().enumeration_items()]
                )
                break
    return types_enum


def refresh_classes(self, context):
    IfcClassData.load()
    enum = get_ifc_classes(self, context)
    context.scene.BIMRootProperties.ifc_class = enum[0][0]


def refreshPredefinedTypes(self, context):
    global types_enum
    types_enum.clear()
    enum = getIfcPredefinedTypes(self, context)
    if enum:
        context.scene.BIMRootProperties.ifc_predefined_type = enum[0][0]


def get_ifc_products(self, context):
    if not IfcClassData.is_loaded:
        IfcClassData.load()
    return IfcClassData.data["ifc_products"]


def get_ifc_classes(self, context):
    if not IfcClassData.is_loaded:
        IfcClassData.load()
    return IfcClassData.data["ifc_classes"]


def get_contexts(self, context):
    if not IfcClassData.is_loaded:
        IfcClassData.load()
    return IfcClassData.data["contexts"]


class BIMRootProperties(PropertyGroup):
    contexts: EnumProperty(items=get_contexts, name="Contexts")
    ifc_product: EnumProperty(items=get_ifc_products, name="Products", update=refresh_classes)
    ifc_class: EnumProperty(items=get_ifc_classes, name="Class", update=refreshPredefinedTypes)
    ifc_predefined_type: EnumProperty(items=getIfcPredefinedTypes, name="Predefined Type", default=None)
    ifc_userdefined_type: StringProperty(name="Userdefined Type")
