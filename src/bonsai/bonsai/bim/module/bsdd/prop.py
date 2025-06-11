# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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
from bpy.types import PropertyGroup
from bonsai.bim.module.bsdd.data import BSDDData
from bonsai.bim.prop import Attribute, StrProperty
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
from typing import Union


def get_active_dictionary(self, context):
    if not BSDDData.is_loaded:
        BSDDData.load()
    return BSDDData.data["active_dictionary"]


def update_is_active(self: "BSDDDictionary", context: bpy.types.Context) -> None:
    BSDDData.data["active_dictionary"] = BSDDData.active_dictionary()


def update_is_selected(self: "BSDDProperty", context: bpy.types.Context) -> None:
    tool.Bsdd.import_selected_properties()


def update_active_class_index(self: "BIMBSDDProperties", context: bpy.types.Context) -> None:
    tool.Bsdd.import_class_properties()
    BSDDData.data["active_dictionary"] = BSDDData.active_dictionary()


class BSDDDictionary(PropertyGroup):
    name: StringProperty(name="Name")
    uri: StringProperty(name="URI")
    default_language_code: StringProperty(name="Language")
    organization_name_owner: StringProperty(name="Organization")
    status: StringProperty(name="Status")
    version: StringProperty(name="Version")
    is_active: BoolProperty(
        name="Is Active", description="Enable to search with this dictionary", default=False, update=update_is_active
    )


class BSDDClassification(PropertyGroup):
    name: StringProperty(name="Name")
    reference_code: StringProperty(name="Reference Code")
    uri: StringProperty(name="URI")
    dictionary_name: StringProperty(name="Dictionary Name")
    dictionary_namespace_uri: StringProperty(name="Dictionary Namespace URI")


class BSDDProperty(PropertyGroup):
    name: StringProperty(name="Name")
    code: StringProperty(name="Code")
    uri: StringProperty(name="URI")
    pset: StringProperty(name="Pset")
    is_selected: BoolProperty(
        name="Is Selected", description="Select to add or edit this property", default=False, update=update_is_selected
    )


class BSDDPset(PropertyGroup):
    name: StringProperty(name="Name")
    properties: CollectionProperty(name="Properties", type=Attribute)


class BIMBSDDProperties(PropertyGroup):
    active_dictionary: StringProperty(name="Active Dictionary")
    active_dictionary: EnumProperty(items=get_active_dictionary, name="Active Dictionary")
    active_uri: StringProperty(name="Active URI")
    dictionaries: CollectionProperty(name="Dictionaries", type=BSDDDictionary)
    active_dictionary_index: IntProperty(name="Active Dictionary Index")
    classifications: CollectionProperty(name="Classifications", type=BSDDClassification)
    active_classification_index: IntProperty(name="Active Classification Index")
    property_filter_mode: EnumProperty(
        name="Property Filter Mode",
        items=[
            ("CLASS", "By Class", "Browse properties by class or group"),
            ("KEYWORD", "By Keyword", "Search properties directly using a keyword"),
        ],
        default="CLASS",
    )
    classes: CollectionProperty(name="Classes", type=BSDDClassification)
    active_class_index: IntProperty(name="Active Class Index", update=update_active_class_index)
    properties: CollectionProperty(name="Properties", type=BSDDProperty)
    active_property_index: IntProperty(name="Active Property Index")
    selected_properties: CollectionProperty(name="Selected Properties", type=Attribute)
    keyword: StringProperty(name="Keyword", description="Query for bsdd classes search, case and accent insensitive")
    should_filter_ifc_class: BoolProperty(
        name="Filter Active IFC Class",
        description="Whether to search only for bSDD classes that match active object's IFC class",
        default=True,
    )
    use_only_ifc_properties: BoolProperty(
        name="Only IFC Properties",
        description="Whether to display and assign only properties from IFC dictionary",
        default=False,
    )
    load_preview_dictionaries: BoolProperty(
        name="Load Preview Dictionaries", description="Load dictionaries marked as Preview status", default=False
    )
    load_inactive_dictionaries: BoolProperty(
        name="Load Inactive Dictionaries", description="Load dictionaries marked as Inactive status", default=False
    )
    load_test_dictionaries: BoolProperty(
        name="Load Test Dictionaries", description="Load dictionaries that are for testing only", default=False
    )
    classification_psets: CollectionProperty(name="Classification Psets", type=BSDDPset)

    @property
    def active_class(self) -> Union[BSDDClassification, None]:
        return tool.Blender.get_active_uilist_element(self.classes, self.active_class_index)
