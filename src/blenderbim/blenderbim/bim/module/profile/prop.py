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
import ifcopenshell.util.attribute
from blenderbim.bim.ifc import IfcStore
from blenderbim.bim.prop import StrProperty, Attribute
from blenderbim.bim.module.profile.data import ProfileData
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


def get_profile_classes(self, context):
    if not ProfileData.is_loaded:
        ProfileData.load()
    return ProfileData.data["profile_classes"]


class Profile(PropertyGroup):
    name: StringProperty(name="Name")
    ifc_class: StringProperty(name="IFC Class")
    ifc_definition_id: IntProperty(name="IFC Definition ID")


class BIMProfileProperties(PropertyGroup):
    is_editing: BoolProperty(name="Is Editing")
    profiles: CollectionProperty(name="Profiles", type=Profile)
    active_profile_index: IntProperty(name="Active Profile Index")
    active_profile_id: IntProperty(name="Active Profile Id")
    profile_attributes: CollectionProperty(name="Profile Attributes", type=Attribute)
    profile_classes: EnumProperty(items=get_profile_classes, name="Profile Classes")
