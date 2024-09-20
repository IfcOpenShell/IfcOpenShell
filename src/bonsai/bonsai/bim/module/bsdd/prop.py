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
from bpy.types import PropertyGroup
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


class BSDDDomain(PropertyGroup):
    name: StringProperty(name="Name")
    uri: StringProperty(name="URI")
    default_language_code: StringProperty(name="Language")
    organization_name_owner: StringProperty(name="Organization")
    status: StringProperty(name="Status")
    version: StringProperty(name="Version")


class BSDDClassification(PropertyGroup):
    name: StringProperty(name="Name")
    reference_code: StringProperty(name="Reference Code")
    uri: StringProperty(name="Namespace URI")
    domain_name: StringProperty(name="Domain Name")
    domain_namespace_uri: StringProperty(name="Domain Namespace URI")


class BSDDPset(PropertyGroup):
    name: StringProperty(name="Name")
    properties: CollectionProperty(name="Properties", type=Attribute)


class BIMBSDDProperties(PropertyGroup):
    active_domain: StringProperty(name="Active Domain")
    active_uri: StringProperty(name="Active URI")
    domains: CollectionProperty(name="Domains", type=BSDDDomain)
    active_domain_index: IntProperty(name="Active Domain Index")
    classifications: CollectionProperty(name="Classifications", type=BSDDClassification)
    active_classification_index: IntProperty(name="Active Classification Index")
    keyword: StringProperty(name="Keyword", description="Query for bsdd classes search, case and accent insensitive")
    should_filter_ifc_class: BoolProperty(
        name="Filter Active IFC Class",
        description="Whether to search only for bSDD classes that match active object's IFC class",
        default=True,
    )
    use_only_ifc_properties: BoolProperty(
        name="Only IFC Properties",
        description="Whether to display and assign only properties from IFC dictionary",
        default=True,
    )
    load_preview_domains: BoolProperty(
        name="Load Preview Domains", description="Whether it should load preview and inactive domains", default=False
    )
    classification_psets: CollectionProperty(name="Classification Psets", type=BSDDPset)
