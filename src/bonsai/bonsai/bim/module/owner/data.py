# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
from ifcopenshell.util.doc import get_entity_doc


def refresh():
    PeopleData.is_loaded = False
    OrganisationsData.is_loaded = False
    OwnerData.is_loaded = False
    ActorData.is_loaded = False
    ObjectActorData.is_loaded = False


class RolesAddressesData:
    @classmethod
    def get_roles(cls, parent):
        results = []
        for role in parent.Roles or []:
            results.append(
                {
                    "id": role.id(),
                    "is_editing": bpy.context.scene.BIMOwnerProperties.active_role_id == role.id(),
                    "label": role.UserDefinedRole or role.Role,
                    "props": bpy.context.scene.BIMOwnerProperties.role_attributes,
                }
            )
        return results

    @classmethod
    def get_addresses(cls, parent):
        results = []
        for address in parent.Addresses or []:
            results.append(
                {
                    "id": address.id(),
                    "is_editing": bpy.context.scene.BIMOwnerProperties.active_address_id == address.id(),
                    "label": address.is_a(),
                    "props": bpy.context.scene.BIMOwnerProperties.address_attributes,
                    "list_attributes": cls.get_address_list_attributes(address),
                }
            )
        return results

    @classmethod
    def get_address_list_attributes(cls, address):
        results = []
        props = bpy.context.scene.BIMOwnerProperties
        if address.is_a("IfcPostalAddress"):
            names = ["AddressLines"]
        elif address.is_a("IfcTelecomAddress"):
            names = ["TelephoneNumbers", "FacsimileNumbers", "ElectronicMailAddresses", "MessagingIDs"]
        for name in names:
            if name == "AddressLines":
                items = [{"id": id, "prop": prop} for id, prop in enumerate(props.address_lines)]
            elif name == "TelephoneNumbers":
                items = [{"id": id, "prop": prop} for id, prop in enumerate(props.telephone_numbers)]
            elif name == "FacsimileNumbers":
                items = [{"id": id, "prop": prop} for id, prop in enumerate(props.facsimile_numbers)]
            elif name == "ElectronicMailAddresses":
                items = [{"id": id, "prop": prop} for id, prop in enumerate(props.electronic_mail_addresses)]
            elif name == "MessagingIDs":
                items = [{"id": id, "prop": prop} for id, prop in enumerate(props.messaging_ids)]
            results.append({"name": name, "items": items})
        return results


class PeopleData(RolesAddressesData):
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"people": cls.get_people()}
        cls.is_loaded = True

    @classmethod
    def get_people(cls):
        people = []
        for person in tool.Ifc.get().by_type("IfcPerson"):
            roles = cls.get_roles(person)
            people.append(
                {
                    "id": person.id(),
                    "props": bpy.context.scene.BIMOwnerProperties.person_attributes,
                    "name": cls.get_person_name(person),
                    "roles_label": ", ".join([r["label"] for r in roles]),
                    "is_editing": cls.get_person_is_editing(person),
                    "is_engaged": bool(person.EngagedIn),
                    "list_attributes": cls.get_person_list_attributes(person),
                    "roles": roles,
                    "addresses": cls.get_addresses(person),
                }
            )
        return people

    @classmethod
    def get_person_name(cls, person):
        if tool.Ifc.get_schema() == "IFC2X3":
            name = person.Id
        else:
            name = person.Identification
        name = name or "*"
        if person.GivenName or person.FamilyName:
            full_name = "{} {}".format(person.GivenName or "", person.FamilyName or "").strip()
            name += f" ({full_name})"
        return name

    @classmethod
    def get_person_is_editing(cls, person):
        return bpy.context.scene.BIMOwnerProperties.active_person_id == person.id()

    @classmethod
    def get_person_list_attributes(cls, person):
        results = []
        props = bpy.context.scene.BIMOwnerProperties
        for name in ["MiddleNames", "PrefixTitles", "SuffixTitles"]:
            if name == "MiddleNames":
                items = [{"id": id, "prop": prop} for id, prop in enumerate(props.middle_names)]
            elif name == "PrefixTitles":
                items = [{"id": id, "prop": prop} for id, prop in enumerate(props.prefix_titles)]
            elif name == "SuffixTitles":
                items = [{"id": id, "prop": prop} for id, prop in enumerate(props.suffix_titles)]
            results.append({"name": name, "items": items})
        return results


class OrganisationsData(RolesAddressesData):
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"organisations": cls.get_organisations()}
        cls.is_loaded = True

    @classmethod
    def get_organisations(cls):
        organisations = []
        for organisation in tool.Ifc.get().by_type("IfcOrganization"):
            roles = cls.get_roles(organisation)
            organisations.append(
                {
                    "id": organisation.id(),
                    "props": bpy.context.scene.BIMOwnerProperties.organisation_attributes,
                    "name": organisation.Name,
                    "roles_label": ", ".join([r["label"] for r in roles]),
                    "is_editing": bpy.context.scene.BIMOwnerProperties.active_organisation_id == organisation.id(),
                    "is_engaged": bool(organisation.Engages),
                    "roles": roles,
                    "addresses": cls.get_addresses(organisation),
                }
            )
        return organisations


class OwnerData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "user_person": cls.get_user_person(),
            "user_organisation": cls.get_user_organisation(),
            "can_add_user": cls.can_add_user(),
            "users": cls.get_users(),
        }
        cls.is_loaded = True

    @classmethod
    def get_user_person(cls):
        return [(str(p.id()), p[0] or "Unnamed", "") for p in tool.Ifc.get().by_type("IfcPerson")]

    @classmethod
    def get_user_organisation(cls):
        return [(str(p.id()), p[0] or "Unnamed", "") for p in tool.Ifc.get().by_type("IfcOrganization")]

    @classmethod
    def can_add_user(cls):
        return tool.Ifc.get().by_type("IfcPerson") and tool.Ifc.get().by_type("IfcOrganization")

    @classmethod
    def get_users(cls):
        results = []
        for user in tool.Ifc.get().by_type("IfcPersonAndOrganization"):
            results.append(
                {
                    "id": user.id(),
                    "label": "{} ({})".format(user.ThePerson[0] or "Unnamed", user.TheOrganization[0] or "Unnamed"),
                    "is_active": bpy.context.scene.BIMOwnerProperties.active_user_id == user.id(),
                }
            )
        return results


class ActorData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "the_actor": cls.the_actor(),
            "actors": cls.actors(),
            "actor_class_enum": cls.actor_class_enum(),
            "get_actor_type_enum": cls.get_actor_type_enum(),
        }
        cls.is_loaded = True

    @classmethod
    def the_actor(cls):
        ifc_class = bpy.context.scene.BIMOwnerProperties.actor_type
        return [(str(p.id()), p[0] or "Unnamed", "") for p in tool.Ifc.get().by_type(ifc_class)]

    @classmethod
    def actors(cls):
        actors = []
        props = bpy.context.scene.BIMOwnerProperties
        for actor in tool.Ifc.get().by_type(props.actor_class, include_subtypes=False):
            is_editing = props.active_actor_id == actor.id()
            if actor.TheActor.is_a("IfcPerson"):
                the_actor = actor.TheActor.Identification or "N/A"
            elif actor.TheActor.is_a("IfcOrganization"):
                the_actor = actor.TheActor.Identification or "N/A"
            elif actor.TheActor.is_a("IfcPersonAndOrganization"):
                the_actor = actor.TheActor.ThePerson.Identification or "N/A"
                the_actor += "-" + actor.TheActor.TheOrganization.Identification or "N/A"
            actors.append(
                {"id": actor.id(), "name": actor.Name or "Unnamed", "the_actor": the_actor, "is_editing": is_editing}
            )
        return actors

    @classmethod
    def actor_class_enum(cls) -> list[tuple[str, str, str]]:
        version = tool.Ifc.get_schema()
        return [
            ("IfcActor", "Actor", get_entity_doc(version, "IfcActor").get("description", "")),
            ("IfcOccupant", "Occupant", get_entity_doc(version, "IfcOccupant").get("description", "")),
        ]

    @classmethod
    def get_actor_type_enum(cls) -> list[tuple[str, str, str]]:
        version = tool.Ifc.get_schema()
        return [
            ("IfcPerson", "Person", get_entity_doc(version, "IfcPerson").get("description", "")),
            ("IfcOrganization", "Organisation", get_entity_doc(version, "IfcOrganization").get("description", "")),
            (
                "IfcPersonAndOrganization",
                "User",
                get_entity_doc(version, "IfcPersonAndOrganization").get("description", ""),
            ),
        ]


class ObjectActorData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {"actor": cls.actor(), "actors": cls.actors()}

    @classmethod
    def actor(cls):
        return [(str(p.id()), p.Name or "Unnamed", "") for p in tool.Ifc.get().by_type("IfcActor")]

    @classmethod
    def actors(cls):
        results = []
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if not element:
            return results
        for rel in getattr(element, "HasAssignments", []):
            if rel.is_a("IfcRelAssignsToActor"):
                actor = rel.RelatingActor
                if actor.TheActor.is_a("IfcPerson"):
                    roles = cls.get_roles(actor.TheActor)
                elif actor.TheActor.is_a("IfcOrganization"):
                    roles = cls.get_roles(actor.TheActor)
                elif actor.TheActor.is_a("IfcPersonAndOrganization"):
                    roles = cls.get_roles(actor.TheActor.ThePerson)
                    roles.extend(cls.get_roles(actor.TheActor.TheOrganization))
                role = ", ".join(roles)
                results.append(
                    {"id": actor.id(), "name": actor.Name or "Unnamed", "role": role, "ifc_class": actor.is_a()}
                )
        return results

    @classmethod
    def get_roles(cls, parent):
        return [r.UserDefinedRole or r.Role for r in parent.Roles or []]
