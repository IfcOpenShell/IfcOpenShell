# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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
import blenderbim.tool as tool


class PeopleData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"people": cls.get_people()}
        cls.is_loaded = True

    @classmethod
    def get_people(cls):
        people = []
        for person in tool.Ifc().get().by_type("IfcPerson"):
            people.append(
                {
                    "id": person.id(),
                    "props": bpy.context.scene.BIMOwnerProperties.person_attributes,
                    "name": cls.get_person_name(person),
                    "is_editing": cls.get_person_is_editing(person),
                    "is_engaged": bool(person.EngagedIn),
                    "list_attributes": cls.get_person_list_attributes(person),
                    "roles": cls.get_person_roles(person),
                    "addresses": cls.get_person_addresses(person),
                }
            )
        return people

    @classmethod
    def get_person_name(cls, person):
        if tool.Ifc().get_schema() == "IFC2X3":
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

    @classmethod
    def get_person_roles(cls, person):
        results = []
        for role in person.Roles or []:
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
    def get_person_addresses(cls, person):
        results = []
        for address in person.Addresses or []:
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
