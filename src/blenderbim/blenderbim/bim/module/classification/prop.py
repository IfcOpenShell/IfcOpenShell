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
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.prop import StrProperty, Attribute
from blenderbim.bim.module.classification.data import ClassificationsData
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


class ClassificationReference(PropertyGroup):
    name: StringProperty(name="Name")
    identification: StringProperty(name="Identification")
    ifc_definition_id: IntProperty(name="IFC Definition ID")
    has_references: BoolProperty(name="Has References")
    referenced_source: IntProperty(name="IFC Definition ID")


class BIMClassificationProperties(PropertyGroup):
    available_classifications: EnumProperty(items=get_available_classifications, name="Available Classifications")
    classification_attributes: CollectionProperty(name="Classification Attributes", type=Attribute)
    active_classification_id: IntProperty(name="Active Classification Id")
    available_library_references: CollectionProperty(name="Available Library References", type=ClassificationReference)
    active_library_referenced_source: IntProperty(name="Active Library Referenced Source")
    active_library_reference_index: IntProperty(name="Active Library Reference Index")


class BIMClassificationReferenceProperties(PropertyGroup):
    reference_attributes: CollectionProperty(name="Reference Attributes", type=Attribute)
    active_reference_id: IntProperty(name="Active Reference Id")
