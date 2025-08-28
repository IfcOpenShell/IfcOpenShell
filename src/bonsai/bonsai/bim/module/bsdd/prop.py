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
from bonsai.bim.module.classification.data import ClassificationsData
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
from typing import Union, TYPE_CHECKING, Literal


def get_active_dictionary(self: "BIMBSDDProperties", context: object) -> tool.Blender.BLENDER_ENUM_ITEMS:
    if not BSDDData.is_loaded:
        BSDDData.load()
    return BSDDData.data["active_dictionary"]


def update_is_active(self: "BSDDDictionary", context: bpy.types.Context) -> None:
    tool.Bsdd.save_active_bsdd_to_ifc()

    BSDDData.data["active_dictionary"] = BSDDData.active_dictionary()
    if ClassificationsData.is_loaded:
        props = tool.Classification.get_classification_props()
        # Preserve original enum value.
        classification_source = props.classification_source
        ClassificationsData.data["classification_source"] = ClassificationsData.classification_source()

        # Try to restore enum value.
        if "classification_source" not in props:
            # It's already on the default value, nothing to restore.
            return
        try:
            props.classification_source = classification_source
        except TypeError:
            # Item is no longer active and not present in enum, fallback to the default.
            del props["classification_source"]


def update_is_selected(self: "BSDDProperty", context: bpy.types.Context) -> None:
    tool.Bsdd.import_selected_properties()


def update_active_class_index(self: "BIMBSDDProperties", context: bpy.types.Context) -> None:
    tool.Bsdd.import_class_properties()
    BSDDData.data["active_dictionary"] = BSDDData.active_dictionary()


class BSDDDictionary(PropertyGroup):
    uri: StringProperty(name="URI")
    default_language_code: StringProperty(name="Language")
    organization_name_owner: StringProperty(name="Organization")
    status: StringProperty(name="Status")
    version: StringProperty(name="Version")
    is_active: BoolProperty(
        name="Is Active",
        description="Enable to search with this dictionary",
        default=False,
        update=update_is_active,
    )

    if TYPE_CHECKING:
        uri: str
        default_language_code: str
        organization_name_owner: str
        status: str
        version: str
        is_active: bool


class BSDDClassification(PropertyGroup):
    reference_code: StringProperty(name="Reference Code")
    uri: StringProperty(name="URI")
    dictionary_name: StringProperty(name="Dictionary Name")
    dictionary_namespace_uri: StringProperty(name="Dictionary Namespace URI")

    if TYPE_CHECKING:
        reference_code: str
        uri: str
        dictionary_name: str
        dictionary_namespace_uri: str


class BSDDProperty(PropertyGroup):
    code: StringProperty(name="Code")
    uri: StringProperty(name="URI")
    pset: StringProperty(name="Pset")
    is_selected: BoolProperty(
        name="Is Selected", description="Select to add or edit this property", default=False, update=update_is_selected
    )

    if TYPE_CHECKING:
        code: str
        uri: str
        pset: str
        is_selected: bool


class BSDDPset(PropertyGroup):
    properties: CollectionProperty(name="Properties", type=Attribute)

    if TYPE_CHECKING:
        properties: bpy.types.bpy_prop_collection_idprop[Attribute]


class BIMBSDDProperties(PropertyGroup):
    # TODO: `active_dictionary` is not used anywhere?
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
    classification_psets: CollectionProperty(name="Classification Psets", type=BSDDPset)

    if TYPE_CHECKING:
        active_dictionary: str
        active_dictionary: str
        active_uri: str
        dictionaries: bpy.types.bpy_prop_collection_idprop[BSDDDictionary]
        active_dictionary_index: int
        classifications: bpy.types.bpy_prop_collection_idprop[BSDDClassification]
        active_classification_index: int
        property_filter_mode: Literal["CLASS", "KEYWORD"]
        classes: bpy.types.bpy_prop_collection_idprop[BSDDClassification]
        active_class_index: int
        properties: bpy.types.bpy_prop_collection_idprop[BSDDProperty]
        active_property_index: int
        selected_properties: bpy.types.bpy_prop_collection_idprop[Attribute]
        keyword: str
        should_filter_ifc_class: bool
        use_only_ifc_properties: bool
        classification_psets: bpy.types.bpy_prop_collection_idprop[BSDDPset]

    @property
    def active_class(self) -> Union[BSDDClassification, None]:
        return tool.Blender.get_active_uilist_element(self.classes, self.active_class_index)
