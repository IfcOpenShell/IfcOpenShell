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
from bonsai.bim.prop import StrProperty, Attribute
from bonsai.bim.module.owner.data import OwnerData, ActorData, ObjectActorData
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


def get_user_person(self, context):
    if not OwnerData.is_loaded:
        OwnerData.load()
    return OwnerData.data["user_person"]


def get_user_organisation(self, context):
    if not OwnerData.is_loaded:
        OwnerData.load()
    return OwnerData.data["user_organisation"]


def get_the_actor(self, context):
    if not ActorData.is_loaded:
        ActorData.load()
    return ActorData.data["the_actor"]


def get_actor(self, context):
    if not ObjectActorData.is_loaded:
        ObjectActorData.load()
    return ObjectActorData.data["actor"]


def update_actor_type(self, context):
    ActorData.data["the_actor"] = ActorData.the_actor()


def update_actor_class(self, context):
    ActorData.data["actors"] = ActorData.actors()


def get_actor_class_enum(self, context):
    if not ActorData.is_loaded:
        ActorData.load()
    return ActorData.data["actor_class_enum"]


def get_actor_type_enum(self, context):
    if not ActorData.is_loaded:
        ActorData.load()
    return ActorData.data["actor_type_enum"]


class BIMOwnerProperties(PropertyGroup):
    active_person_id: IntProperty(name="Active Person Id")
    person_attributes: CollectionProperty(name="Person Attributes", type=Attribute)
    middle_names: CollectionProperty(type=StrProperty, name="Middle Names")
    prefix_titles: CollectionProperty(type=StrProperty, name="Prefixes")
    suffix_titles: CollectionProperty(type=StrProperty, name="Suffixes")
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
    user_person: EnumProperty(
        items=get_user_person, name="Person", description="This entity represents an individual human being."
    )
    user_organisation: EnumProperty(
        items=get_user_organisation,
        name="Organisation",
        description="A named and structured grouping with a corporate identity.",
    )
    active_user_id: IntProperty(name="Active User Id")
    active_actor_id: IntProperty(name="Active Actor Id")
    actor_attributes: CollectionProperty(name="Actor Attributes", type=Attribute)
    actor_class: EnumProperty(
        items=get_actor_class_enum,
        name="Actor Type",
        update=update_actor_class,
    )
    actor_type: EnumProperty(
        items=get_actor_type_enum,
        name="Actor Type",
        update=update_actor_type,
    )
    the_actor: EnumProperty(
        items=get_the_actor, name="Actor", description="This entity represents an individual human being."
    )
    actor: EnumProperty(items=get_actor, name="Actor")
