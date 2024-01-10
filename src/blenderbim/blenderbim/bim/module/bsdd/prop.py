# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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
from bpy.types import PropertyGroup
from blenderbim.bim.prop import Attribute, StrProperty
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
    description: StringProperty(name="Description")
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
    keyword: StringProperty(name="Keyword")
    should_filter_ifc_class: BoolProperty(name="Filter Active IFC Class", default=True)
    load_preview_domains: BoolProperty(name="Load Preview Domains", default=False)
    classification_psets: CollectionProperty(name="Classification Psets", type=BSDDPset)
