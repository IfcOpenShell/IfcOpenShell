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


def purge():
    pass


def get_ifc_predefined_types(self, context):
    if not IfcClassData.is_loaded:
        IfcClassData.load()
    return IfcClassData.data["ifc_predefined_types"]


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


class BIMRootProperties(PropertyGroup):
    contexts: EnumProperty(items=get_contexts, name="Contexts")
    ifc_product: EnumProperty(items=get_ifc_products, name="Products", update=refresh_classes)
    ifc_class: EnumProperty(items=get_ifc_classes, name="Class", update=refresh_predefined_types)
    ifc_predefined_type: EnumProperty(items=get_ifc_predefined_types, name="Predefined Type", default=None)
    ifc_userdefined_type: StringProperty(name="Userdefined Type")

    getter_enum_suggestions = {
        "ifc_class": get_ifc_classes_suggestions,
    }
