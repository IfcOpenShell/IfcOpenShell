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
from blenderbim.bim.prop import StrProperty, Attribute
from blenderbim.bim.ifc import IfcStore
from ifcopenshell.api.owner.data import Data
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

_persons_enum = []
_organisations_enum = []


def purge():
    global _persons_enum
    global _organisations_enum
    _persons_enum.clear()
    _organisations_enum.clear()


def getPersons(self, context):
    global _persons_enum
    if not Data.is_loaded:
        Data.load(IfcStore.get_file())
    _persons_enum.clear()
    for ifc_id, person in Data.people.items():
        if "Id" in person:
            identifier = person["Id"] or ""
        else:
            identifier = person["Identification"] or ""
        _persons_enum.append((str(ifc_id), identifier, ""))
    return _persons_enum


def getOrganisations(self, context):
    global _organisations_enum
    if not Data.is_loaded:
        Data.load(IfcStore.get_file())
    _organisations_enum.clear()
    for ifc_id, organisation in Data.organisations.items():
        _organisations_enum.append((str(ifc_id), organisation["Name"], ""))
    return _organisations_enum


class BIMOwnerProperties(PropertyGroup):
    person_attributes: CollectionProperty(name="Person Attributes", type=Attribute)
    middle_names: CollectionProperty(type=StrProperty, name="Middle Names")
    prefix_titles: CollectionProperty(type=StrProperty, name="Prefixes")
    suffix_titles: CollectionProperty(type=StrProperty, name="Suffixes")
    active_person_id: IntProperty(name="Active Person Id")
    active_organisation_id: IntProperty(name="Active Organisation Id")
    organisation_attributes: CollectionProperty(name="Organisation Attributes", type=Attribute)
    active_role_id: IntProperty(name="Active Role Id")
    role_attributes: CollectionProperty(name="Role Attributes", type=Attribute)
    active_address_id: IntProperty(name="Active Address Id")
    address_attributes: CollectionProperty(name="Address Attributes", type=Attribute)
    address_lines: CollectionProperty(type=StrProperty, name="Address")
    telephone_numbers: CollectionProperty(type=StrProperty, name="Telephone Numbers")
    facsimile_numbers: CollectionProperty(type=StrProperty, name="Facsimile Numbers")
    electronic_mail_addresses: CollectionProperty(type=StrProperty, name="Emails")
    messaging_ids: CollectionProperty(type=StrProperty, name="IMs")
    user_person: EnumProperty(items=getPersons, name="Person")
    user_organisation: EnumProperty(items=getOrganisations, name="Organisation")
