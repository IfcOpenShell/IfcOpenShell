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

from __future__ import annotations
import bpy
import bonsai.core.tool
import bonsai.tool as tool
import bonsai.bim.helper
import ifcopenshell
from typing import Union, Any, TYPE_CHECKING, Literal
from typing_extensions import assert_never

if TYPE_CHECKING:
    from bonsai.bim.module.owner.prop import BIMOwnerProperties


class Owner(bonsai.core.tool.Owner):
    @classmethod
    def get_owner_props(cls) -> BIMOwnerProperties:
        return bpy.context.scene.BIMOwnerProperties

    @classmethod
    def set_user(cls, user: ifcopenshell.entity_instance) -> None:
        props = cls.get_owner_props()
        props.active_user_id = user.id()

    @classmethod
    def get_user(cls) -> Union[ifcopenshell.entity_instance, None]:
        props = cls.get_owner_props()
        active_user_id = props.active_user_id
        if active_user_id:
            return tool.Ifc.get().by_id(active_user_id)
        elif tool.Ifc.get_schema() == "IFC2X3":
            users = tool.Ifc.get().by_type("IfcPersonAndOrganization")
            if users:
                return users[0]

    @classmethod
    def clear_user(cls) -> None:
        props = cls.get_owner_props()
        props.active_user_id = 0

    @classmethod
    def set_address(cls, address: ifcopenshell.entity_instance) -> None:
        props = cls.get_owner_props()
        props.active_address_id = address.id()

    @classmethod
    def import_address_attributes(cls) -> None:
        props = props = cls.get_owner_props()
        props.address_attributes.clear()
        props.address_lines.clear()
        props.telephone_numbers.clear()
        props.facsimile_numbers.clear()
        props.electronic_mail_addresses.clear()
        props.messaging_ids.clear()

        address = cls.get_address()

        def callback(name: str, prop, data: dict[str, Any]) -> None:
            if name == "AddressLines":
                for line in data[name] or []:
                    props.address_lines.add().name = line
            elif name == "TelephoneNumbers":
                for line in data[name] or []:
                    props.telephone_numbers.add().name = line
            elif name == "FacsimileNumbers":
                for line in data[name] or []:
                    props.facsimile_numbers.add().name = line
            elif name == "ElectronicMailAddresses":
                for line in data[name] or []:
                    props.electronic_mail_addresses.add().name = line
            elif name == "MessagingIDs":
                for line in data[name] or []:
                    props.messaging_ids.add().name = line

        bonsai.bim.helper.import_attributes(address.is_a(), props.address_attributes, address.get_info(), callback)

    @classmethod
    def clear_address(cls) -> None:
        props = cls.get_owner_props()
        props.active_address_id = 0

    @classmethod
    def get_address(cls) -> ifcopenshell.entity_instance:
        props = cls.get_owner_props()
        return tool.Ifc().get().by_id(props.active_address_id)

    @classmethod
    def export_address_attributes(cls) -> dict[str, Any]:
        props = cls.get_owner_props()
        attributes = bonsai.bim.helper.export_attributes(props.address_attributes)
        if cls.get_address().is_a("IfcPostalAddress"):
            attributes["AddressLines"] = [l.name for l in props.address_lines] or None
        elif cls.get_address().is_a("IfcTelecomAddress"):
            attributes["TelephoneNumbers"] = [l.name for l in props.telephone_numbers] or None
            attributes["FacsimileNumbers"] = [l.name for l in props.facsimile_numbers] or None
            attributes["ElectronicMailAddresses"] = [l.name for l in props.electronic_mail_addresses] or None
            attributes["MessagingIDs"] = [l.name for l in props.messaging_ids] or None
        return attributes

    AddressAttributeType = Literal[
        "AddressLines", "TelephoneNumbers", "FacsimileNumbers", "ElectronicMailAddresses", "MessagingIDs"
    ]

    @classmethod
    def add_address_attribute(cls, name: AddressAttributeType) -> None:
        props = cls.get_owner_props()
        if name == "AddressLines":
            props.address_lines.add()
        elif name == "TelephoneNumbers":
            props.telephone_numbers.add()
        elif name == "FacsimileNumbers":
            props.facsimile_numbers.add()
        elif name == "ElectronicMailAddresses":
            props.electronic_mail_addresses.add()
        elif name == "MessagingIDs":
            props.messaging_ids.add()
        else:
            assert_never(name)

    @classmethod
    def remove_address_attribute(cls, name: AddressAttributeType, id: int) -> None:
        props = cls.get_owner_props()
        if name == "AddressLines":
            props.address_lines.remove(id)
        elif name == "TelephoneNumbers":
            props.telephone_numbers.remove(id)
        elif name == "FacsimileNumbers":
            props.facsimile_numbers.remove(id)
        elif name == "ElectronicMailAddresses":
            props.electronic_mail_addresses.remove(id)
        elif name == "MessagingIDs":
            props.messaging_ids.remove(id)
        else:
            assert_never(name)

    @classmethod
    def set_organisation(cls, organisation: ifcopenshell.entity_instance) -> None:
        props = cls.get_owner_props()
        props.active_organisation_id = organisation.id()

    @classmethod
    def import_organisation_attributes(cls) -> None:
        props = cls.get_owner_props()
        organisation = tool.Ifc.get().by_id(props.active_organisation_id)
        props.organisation_attributes.clear()

        bonsai.bim.helper.import_attributes("IfcOrganization", props.organisation_attributes, organisation.get_info())

    @classmethod
    def clear_organisation(cls) -> None:
        props = cls.get_owner_props()
        props.active_organisation_id = 0

    @classmethod
    def export_organisation_attributes(cls) -> dict[str, Any]:
        props = cls.get_owner_props()
        attributes = bonsai.bim.helper.export_attributes(props.organisation_attributes)
        return attributes

    @classmethod
    def get_organisation(cls) -> ifcopenshell.entity_instance:
        props = cls.get_owner_props()
        return tool.Ifc().get().by_id(props.active_organisation_id)

    @classmethod
    def set_person(cls, person: ifcopenshell.entity_instance) -> None:
        props = cls.get_owner_props()
        props.active_person_id = person.id()

    @classmethod
    def import_person_attributes(cls) -> None:
        props = cls.get_owner_props()
        person = tool.Ifc.get().by_id(props.active_person_id)
        props.person_attributes.clear()
        props.middle_names.clear()
        props.prefix_titles.clear()
        props.suffix_titles.clear()

        def callback(name: str, prop, data: dict[str, Any]) -> None:
            if name == "MiddleNames":
                for name in data["MiddleNames"] or []:
                    props.middle_names.add().name = name or ""
            if name == "PrefixTitles":
                for name in data["PrefixTitles"] or []:
                    props.prefix_titles.add().name = name or ""
            if name == "SuffixTitles":
                for name in data["SuffixTitles"] or []:
                    props.suffix_titles.add().name = name or ""

        bonsai.bim.helper.import_attributes("IfcPerson", props.person_attributes, person.get_info(), callback)

    @classmethod
    def clear_person(cls) -> None:
        props = cls.get_owner_props()
        props.active_person_id = 0

    @classmethod
    def export_person_attributes(cls) -> dict[str, Any]:
        props = cls.get_owner_props()
        attributes = bonsai.bim.helper.export_attributes(props.person_attributes)
        attributes["MiddleNames"] = [v.name for v in props.middle_names] if props.middle_names else None
        attributes["PrefixTitles"] = [v.name for v in props.prefix_titles] if props.prefix_titles else None
        attributes["SuffixTitles"] = [v.name for v in props.suffix_titles] if props.suffix_titles else None
        return attributes

    @classmethod
    def get_person(cls) -> ifcopenshell.entity_instance:
        props = cls.get_owner_props()
        return tool.Ifc().get().by_id(props.active_person_id)

    PersonAttributeType = Literal["MiddleNames", "PrefixTitles", "SuffixTitles"]

    @classmethod
    def add_person_attribute(cls, name: PersonAttributeType) -> None:
        props = cls.get_owner_props()
        if name == "MiddleNames":
            props.middle_names.add()
        elif name == "PrefixTitles":
            props.prefix_titles.add()
        elif name == "SuffixTitles":
            props.suffix_titles.add()
        else:
            assert_never(name)

    @classmethod
    def remove_person_attribute(cls, name: PersonAttributeType, id: int) -> None:
        props = cls.get_owner_props()
        if name == "MiddleNames":
            props.middle_names.remove(id)
        elif name == "PrefixTitles":
            props.prefix_titles.remove(id)
        elif name == "SuffixTitles":
            props.suffix_titles.remove(id)
        else:
            assert_never(name)

    @classmethod
    def set_role(cls, role: ifcopenshell.entity_instance) -> None:
        props = cls.get_owner_props()
        props.active_role_id = role.id()

    @classmethod
    def import_role_attributes(cls) -> None:
        role = cls.get_role()
        props = cls.get_owner_props()
        props.role_attributes.clear()
        bonsai.bim.helper.import_attributes("IfcActorRole", props.role_attributes, role.get_info())

    @classmethod
    def clear_role(cls) -> None:
        props = cls.get_owner_props()
        props.active_role_id = 0

    @classmethod
    def get_role(cls) -> ifcopenshell.entity_instance:
        props = cls.get_owner_props()
        return tool.Ifc().get().by_id(props.active_role_id)

    @classmethod
    def export_role_attributes(cls) -> dict[str, Any]:
        props = cls.get_owner_props()
        return bonsai.bim.helper.export_attributes(props.role_attributes)

    @classmethod
    def set_actor(cls, actor: ifcopenshell.entity_instance) -> None:
        props = cls.get_owner_props()
        props.active_actor_id = actor.id()

    @classmethod
    def import_actor_attributes(cls, actor: ifcopenshell.entity_instance) -> None:
        props = cls.get_owner_props()
        props.actor_attributes.clear()
        bonsai.bim.helper.import_attributes2(actor, props.actor_attributes)

    @classmethod
    def clear_actor(cls) -> None:
        props = cls.get_owner_props()
        props.active_actor_id = 0

    @classmethod
    def export_actor_attributes(cls) -> dict[str, Any]:
        props = cls.get_owner_props()
        attributes = bonsai.bim.helper.export_attributes(props.actor_attributes)
        return attributes

    @classmethod
    def get_actor(cls) -> ifcopenshell.entity_instance:
        props = cls.get_owner_props()
        return tool.Ifc().get().by_id(props.active_actor_id)
