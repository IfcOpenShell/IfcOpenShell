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
from bonsai.bim.prop import Attribute
from bonsai.bim.module.classification.data import ClassificationsData, ClassificationReferencesData
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


def get_available_classifications(self, context):
    if not ClassificationsData.is_loaded:
        ClassificationsData.load()
    return ClassificationsData.data["available_classifications"]


def get_classifications(self, context):
    if not ClassificationReferencesData.is_loaded:
        ClassificationReferencesData.load()
    return ClassificationReferencesData.data["classifications"]


class ClassificationReference(PropertyGroup):
    name: StringProperty(name="Name")
    identification: StringProperty(name="Identification")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    has_references: BoolProperty(name="Has References")
    referenced_source: IntProperty(name="IFC Definition ID")


class BIMClassificationProperties(PropertyGroup):
    is_adding: BoolProperty(name="Is Adding", default=False)
    classification_source: EnumProperty(
        items=[
            ("FILE", "IFC File", ""),
            ("BSDD", "buildingSMART Data Dictionary", ""),
            ("MANUAL", "Manual Entry", ""),
        ],
        name="Classification Source",
        default="FILE",
    )
    available_classifications: EnumProperty(items=get_available_classifications, name="Available Classifications")
    classification_attributes: CollectionProperty(name="Classification Attributes", type=Attribute)
    active_classification_id: IntProperty(name="Active Classification Id")
    available_library_references: CollectionProperty(name="Available Library References", type=ClassificationReference)
    active_library_referenced_source: IntProperty(name="Active Library Referenced Source")
    active_library_reference_index: IntProperty(name="Active Library Reference Index")


class BIMClassificationReferenceProperties(PropertyGroup):
    is_adding: BoolProperty(name="Is Adding", default=False)
    classifications: EnumProperty(items=get_classifications, name="Classifications")
    reference_attributes: CollectionProperty(name="Reference Attributes", type=Attribute)
    active_reference_id: IntProperty(name="Active Reference Id")
