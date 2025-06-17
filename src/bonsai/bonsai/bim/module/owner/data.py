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
import ifcopenshell
import bonsai.tool as tool
from typing import Any, Union
from ifcopenshell.util.doc import get_entity_doc
from natsort import natsorted


def refresh():
    PeopleData.is_loaded = False
    OrganisationsData.is_loaded = False
    OwnerData.is_loaded = False
    ActorData.is_loaded = False
    ObjectActorData.is_loaded = False


class RolesAddressesData:
    @classmethod
    def get_roles(cls, parent: ifcopenshell.entity_instance) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for role in parent.Roles or []:
            results.append(
                {
                    "id": role.id(),
                    "label": role.UserDefinedRole or role.Role,
                }
            )
        return results

    @classmethod
    def get_addresses(cls, parent: ifcopenshell.entity_instance) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for address in parent.Addresses or []:
            results.append(
                {
                    "id": address.id(),
                    "label": address.is_a(),
                    "list_attributes": cls.get_address_list_attributes(address),
                }
            )
        return results

    @classmethod
    def get_address_list_attributes(cls, address: ifcopenshell.entity_instance) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        props = tool.Owner.get_owner_props()
        if address.is_a("IfcPostalAddress"):
            names = ["AddressLines"]
        elif address.is_a("IfcTelecomAddress"):
            names = ["TelephoneNumbers", "FacsimileNumbers", "ElectronicMailAddresses", "MessagingIDs"]
        else:
            assert False, f"Unexpected entity: {address}"
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
            else:
                assert False, f"Unexpected name: {name}"
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
    def get_people(cls) -> list[dict[str, Any]]:
        people: list[dict[str, Any]] = []
        for person in tool.Ifc.get().by_type("IfcPerson"):
            roles = cls.get_roles(person)
            people.append(
                {
                    "id": person.id(),
                    "name": cls.get_person_name(person),
                    "roles_label": ", ".join([r["label"] for r in roles]),
                    "is_engaged": bool(person.EngagedIn),
                    "list_attributes": cls.get_person_list_attributes(person),
                    "roles": roles,
                    "addresses": cls.get_addresses(person),
                }
            )
        return people

    @classmethod
    def get_person_name(cls, person: ifcopenshell.entity_instance) -> str:
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
    def get_person_list_attributes(cls, person: ifcopenshell.entity_instance) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        props = tool.Owner.get_owner_props()
        name: tool.Owner.PersonAttributeType
        for name in ("MiddleNames", "PrefixTitles", "SuffixTitles"):
            if name == "MiddleNames":
                items = [{"id": id, "prop": prop} for id, prop in enumerate(props.middle_names)]
            elif name == "PrefixTitles":
                items = [{"id": id, "prop": prop} for id, prop in enumerate(props.prefix_titles)]
            elif name == "SuffixTitles":
                items = [{"id": id, "prop": prop} for id, prop in enumerate(props.suffix_titles)]
            else:
                assert False, name
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
    def get_organisations(cls) -> list[dict[str, Any]]:
        organisations: list[dict[str, Any]] = []
        for organisation in tool.Ifc.get().by_type("IfcOrganization"):
            roles = cls.get_roles(organisation)
            organisations.append(
                {
                    "id": organisation.id(),
                    "name": organisation.Name,
                    "roles_label": ", ".join([r["label"] for r in roles]),
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
    def get_user_person(cls) -> tool.Blender.BLENDER_ENUM_ITEMS:
        return [(str(p.id()), p[0] or "Unnamed", "") for p in tool.Ifc.get().by_type("IfcPerson")]

    @classmethod
    def get_user_organisation(cls) -> tool.Blender.BLENDER_ENUM_ITEMS:
        return [(str(p.id()), p[0] or "Unnamed", "") for p in tool.Ifc.get().by_type("IfcOrganization")]

    @classmethod
    def can_add_user(cls) -> bool:
        return bool(tool.Ifc.get().by_type("IfcPerson") and tool.Ifc.get().by_type("IfcOrganization"))

    @classmethod
    def get_users(cls) -> list[dict[str, Any]]:
        props = tool.Owner.get_owner_props()
        results: list[dict[str, Any]] = []
        for user in tool.Ifc.get().by_type("IfcPersonAndOrganization"):
            results.append(
                {
                    "id": user.id(),
                    "label": "{} ({})".format(user.ThePerson[0] or "Unnamed", user.TheOrganization[0] or "Unnamed"),
                    "is_active": props.active_user_id == user.id(),
                }
            )
        return results


class ActorData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data["actor_class"] = cls.actor_class()
        cls.data["actor_type"] = cls.actor_type()
        cls.data["the_actor"] = cls.the_actor()
        cls.data["actors"] = cls.actors()

    @classmethod
    def the_actor(cls) -> tool.Blender.BLENDER_ENUM_ITEMS:
        props = tool.Owner.get_owner_props()
        if not (ifc_class := props.actor_type):
            ifc_class = cls.actor_type()[0][0]
        return [(str(p.id()), p[0] or "Unnamed", "") for p in tool.Ifc.get().by_type(ifc_class)]

    @classmethod
    def actors(cls) -> list[dict[str, Any]]:
        actors: list[dict[str, Any]] = []
        props = tool.Owner.get_owner_props()
        for actor in tool.Ifc.get().by_type(props.actor_class, include_subtypes=False):
            the_actor: ifcopenshell.entity_instance = actor.TheActor
            if the_actor.is_a("IfcPerson"):
                the_actor_ = the_actor.Identification or "N/A"
            elif the_actor.is_a("IfcOrganization"):
                the_actor_ = the_actor.Identification or "N/A"
            elif the_actor.is_a("IfcPersonAndOrganization"):
                the_actor_ = the_actor.ThePerson.Identification or "N/A"
                the_actor_ += "-" + the_actor.TheOrganization.Identification or "N/A"
            else:
                assert False, the_actor
            actors.append(
                {
                    "id": actor.id(),
                    "name": actor.Name or "Unnamed",
                    "the_actor": the_actor_,
                }
            )
        return actors

    @classmethod
    def actor_class(cls) -> tool.Blender.BLENDER_ENUM_ITEMS:
        version = tool.Ifc.get_schema()
        actor_doc = get_entity_doc(version, "IfcActor")
        occupant_doc = get_entity_doc(version, "IfcOccupant")
        assert actor_doc and occupant_doc
        return [
            ("IfcActor", "Actor", actor_doc.get("description", "")),
            ("IfcOccupant", "Occupant", occupant_doc.get("description", "")),
        ]

    @classmethod
    def actor_type(cls) -> tool.Blender.BLENDER_ENUM_ITEMS:
        version = tool.Ifc.get_schema()
        person_doc = get_entity_doc(version, "IfcPerson")
        organization_doc = get_entity_doc(version, "IfcOrganization")
        pao_doc = get_entity_doc(version, "IfcPersonAndOrganization")
        assert person_doc and organization_doc and pao_doc
        return [
            ("IfcPerson", "Person", person_doc.get("description", "")),
            ("IfcOrganization", "Organisation", organization_doc.get("description", "")),
            ("IfcPersonAndOrganization", "User", pao_doc.get("description", "")),
        ]


class ObjectActorData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data = {"actor": cls.actor(), "actors": cls.actors()}

    @classmethod
    def actor(cls) -> tool.Blender.BLENDER_ENUM_ITEMS:
        return [(str(p.id()), p.Name or "Unnamed", "") for p in tool.Ifc.get().by_type("IfcActor")]

    @classmethod
    def actors(cls) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        obj = bpy.context.active_object
        if not obj:
            return results
        element = tool.Ifc.get_entity(obj)
        if not element:
            return results
        for rel in getattr(element, "HasAssignments", []):
            if rel.is_a("IfcRelAssignsToActor"):
                actor = rel.RelatingActor
                the_actor: ifcopenshell.entity_instance = actor.TheActor
                if the_actor.is_a("IfcPerson"):
                    roles = cls.get_roles(the_actor)
                elif the_actor.is_a("IfcOrganization"):
                    roles = cls.get_roles(the_actor)
                elif the_actor.is_a("IfcPersonAndOrganization"):
                    roles = cls.get_roles(the_actor.ThePerson)
                    roles.extend(cls.get_roles(the_actor.TheOrganization))
                else:
                    assert False, the_actor
                role = ", ".join(roles)
                results.append(
                    {"id": actor.id(), "name": actor.Name or "Unnamed", "role": role, "ifc_class": actor.is_a()}
                )
        return results

    @classmethod
    def get_roles(cls, parent: ifcopenshell.entity_instance) -> list[Union[str, None]]:
        return [r.UserDefinedRole or r.Role for r in parent.Roles or []]


class ApplicationsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls) -> None:
        cls.is_loaded = True
        cls.data = {
            "applications": cls.applications(),
        }

    @classmethod
    def applications(cls) -> list[dict[str, Any]]:
        applications: list[dict[str, Any]] = []
        ifc_file = tool.Ifc.get()
        for application in ifc_file.by_type("IfcApplication"):
            total_inverses = ifc_file.get_total_inverses(application)
            name = application.ApplicationFullName
            if total_inverses == 0:
                name += " (unused)"
            applications.append(
                {
                    "id": application.id(),
                    "name": name,
                }
            )
        return natsorted(applications, key=lambda x: x["name"])
