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
import bonsai.tool as tool
from bonsai.bim.prop import Attribute
from bonsai.bim.module.classification.data import ClassificationsData, ObjectClassificationsData
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
from typing import TYPE_CHECKING


def get_available_classifications(
    self: "BIMClassificationProperties", context: bpy.types.Context
) -> tool.Blender.BLENDER_ENUM_ITEMS:
    if not ClassificationsData.is_loaded:
        ClassificationsData.load()
    return ClassificationsData.data["available_classifications"]


def get_classifications(self, context):
    if not ObjectClassificationsData.is_loaded:
        ObjectClassificationsData.load()
    return ObjectClassificationsData.data["classifications"]


def get_classification_source(
    self: "BIMClassificationProperties", context: bpy.types.Context
) -> tool.Blender.BLENDER_ENUM_ITEMS:
    if not ClassificationsData.is_loaded:
        ClassificationsData.load()
    return ClassificationsData.data["classification_source"]


class ClassificationReference(PropertyGroup):
    identification: StringProperty(name="Identification")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    has_references: BoolProperty(name="Has References")
    referenced_source: IntProperty(name="IFC Definition ID")

    if TYPE_CHECKING:
        identification: str
        ifc_definition_id: int
        has_references: bool
        referenced_source: int


class BIMClassificationProperties(PropertyGroup):
    is_adding: BoolProperty(name="Is Adding", default=False)
    classification_source: EnumProperty(items=get_classification_source, name="Classification Source")
    available_classifications: EnumProperty(items=get_available_classifications, name="Available Classifications")
    classification_attributes: CollectionProperty(name="Classification Attributes", type=Attribute)
    active_classification_id: IntProperty(name="Active Classification Id")
    available_library_references: CollectionProperty(name="Available Library References", type=ClassificationReference)
    active_library_referenced_source: IntProperty(name="Active Library Referenced Source")
    active_library_reference_index: IntProperty(name="Active Library Reference Index")

    if TYPE_CHECKING:
        is_adding: bool
        classification_source: str
        available_classifications: str
        classification_attributes: bpy.types.bpy_prop_collection_idprop[Attribute]
        active_classification_id: int
        available_library_references: bpy.types.bpy_prop_collection_idprop[ClassificationReference]
        active_library_referenced_source: int
        active_library_reference_index: int


class BIMClassificationReferenceProperties(PropertyGroup):
    is_adding: BoolProperty(name="Is Adding", default=False)
    classifications: EnumProperty(items=get_classifications, name="Classifications")
    reference_attributes: CollectionProperty(name="Reference Attributes", type=Attribute)
    active_reference_id: IntProperty(name="Active Reference Id")

    if TYPE_CHECKING:
        is_adding: bool
        classifications: str
        reference_attributes: bpy.types.bpy_prop_collection_idprop
        active_reference_id: int
