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
import blenderbim.core.tool
import blenderbim.tool as tool
import ifcopenshell
from typing import Union


class Owner(blenderbim.core.tool.Owner):
    @classmethod
    def set_user(cls, user):
        bpy.context.scene.BIMOwnerProperties.active_user_id = user.id()

    @classmethod
    def get_user(cls) -> Union[ifcopenshell.entity_instance, None]:
        if bpy.context.scene.BIMOwnerProperties.active_user_id:
            return tool.Ifc.get().by_id(bpy.context.scene.BIMOwnerProperties.active_user_id)
        elif tool.Ifc.get_schema() == "IFC2X3":
            users = tool.Ifc.get().by_type("IfcPersonAndOrganization")
            if users:
                return users[0]

    @classmethod
    def clear_user(cls):
        bpy.context.scene.BIMOwnerProperties.active_user_id = 0

    @classmethod
    def set_address(cls, address):
        bpy.context.scene.BIMOwnerProperties.active_address_id = address.id()

    @classmethod
    def import_address_attributes(cls):
        props = bpy.context.scene.BIMOwnerProperties
        props.address_attributes.clear()
        props.address_lines.clear()
        props.telephone_numbers.clear()
        props.facsimile_numbers.clear()
        props.electronic_mail_addresses.clear()
        props.messaging_ids.clear()

        address = cls.get_address()

        def callback(name, prop, data):
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

        blenderbim.bim.helper.import_attributes(address.is_a(), props.address_attributes, address.get_info(), callback)

    @classmethod
    def clear_address(cls):
        bpy.context.scene.BIMOwnerProperties.active_address_id = 0

    @classmethod
    def get_address(cls):
        return tool.Ifc().get().by_id(bpy.context.scene.BIMOwnerProperties.active_address_id)

    @classmethod
    def export_address_attributes(cls):
        props = bpy.context.scene.BIMOwnerProperties
        attributes = blenderbim.bim.helper.export_attributes(props.address_attributes)
        if cls.get_address().is_a("IfcPostalAddress"):
            attributes["AddressLines"] = [l.name for l in props.address_lines] or None
        elif cls.get_address().is_a("IfcTelecomAddress"):
            attributes["TelephoneNumbers"] = [l.name for l in props.telephone_numbers] or None
            attributes["FacsimileNumbers"] = [l.name for l in props.facsimile_numbers] or None
            attributes["ElectronicMailAddresses"] = [l.name for l in props.electronic_mail_addresses] or None
            attributes["MessagingIDs"] = [l.name for l in props.messaging_ids] or None
        return attributes

    @classmethod
    def add_address_attribute(cls, name):
        props = bpy.context.scene.BIMOwnerProperties
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

    @classmethod
    def remove_address_attribute(cls, name, id):
        props = bpy.context.scene.BIMOwnerProperties
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

    @classmethod
    def set_organisation(cls, organisation):
        bpy.context.scene.BIMOwnerProperties.active_organisation_id = organisation.id()

    @classmethod
    def import_organisation_attributes(cls):
        organisation = tool.Ifc.get().by_id(bpy.context.scene.BIMOwnerProperties.active_organisation_id)
        props = bpy.context.scene.BIMOwnerProperties
        props.organisation_attributes.clear()

        blenderbim.bim.helper.import_attributes(
            "IfcOrganization", props.organisation_attributes, organisation.get_info()
        )

    @classmethod
    def clear_organisation(cls):
        bpy.context.scene.BIMOwnerProperties.active_organisation_id = 0

    @classmethod
    def export_organisation_attributes(cls):
        props = bpy.context.scene.BIMOwnerProperties
        attributes = blenderbim.bim.helper.export_attributes(props.organisation_attributes)
        return attributes

    @classmethod
    def get_organisation(cls):
        return tool.Ifc().get().by_id(bpy.context.scene.BIMOwnerProperties.active_organisation_id)

    @classmethod
    def set_person(cls, person):
        bpy.context.scene.BIMOwnerProperties.active_person_id = person.id()

    @classmethod
    def import_person_attributes(cls):
        person = tool.Ifc.get().by_id(bpy.context.scene.BIMOwnerProperties.active_person_id)
        props = bpy.context.scene.BIMOwnerProperties
        props.person_attributes.clear()
        props.middle_names.clear()
        props.prefix_titles.clear()
        props.suffix_titles.clear()

        def callback(name, prop, data):
            if name == "MiddleNames":
                for name in data["MiddleNames"] or []:
                    props.middle_names.add().name = name or ""
            if name == "PrefixTitles":
                for name in data["PrefixTitles"] or []:
                    props.prefix_titles.add().name = name or ""
            if name == "SuffixTitles":
                for name in data["SuffixTitles"] or []:
                    props.suffix_titles.add().name = name or ""

        blenderbim.bim.helper.import_attributes("IfcPerson", props.person_attributes, person.get_info(), callback)

    @classmethod
    def clear_person(cls):
        bpy.context.scene.BIMOwnerProperties.active_person_id = 0

    @classmethod
    def export_person_attributes(cls):
        props = bpy.context.scene.BIMOwnerProperties
        attributes = blenderbim.bim.helper.export_attributes(props.person_attributes)
        attributes["MiddleNames"] = [v.name for v in props.middle_names] if props.middle_names else None
        attributes["PrefixTitles"] = [v.name for v in props.prefix_titles] if props.prefix_titles else None
        attributes["SuffixTitles"] = [v.name for v in props.suffix_titles] if props.suffix_titles else None
        return attributes

    @classmethod
    def get_person(cls):
        return tool.Ifc().get().by_id(bpy.context.scene.BIMOwnerProperties.active_person_id)

    @classmethod
    def add_person_attribute(cls, name):
        if name == "MiddleNames":
            bpy.context.scene.BIMOwnerProperties.middle_names.add()
        elif name == "PrefixTitles":
            bpy.context.scene.BIMOwnerProperties.prefix_titles.add()
        elif name == "SuffixTitles":
            bpy.context.scene.BIMOwnerProperties.suffix_titles.add()

    @classmethod
    def remove_person_attribute(cls, name, id):
        if name == "MiddleNames":
            bpy.context.scene.BIMOwnerProperties.middle_names.remove(id)
        elif name == "PrefixTitles":
            bpy.context.scene.BIMOwnerProperties.prefix_titles.remove(id)
        elif name == "SuffixTitles":
            bpy.context.scene.BIMOwnerProperties.suffix_titles.remove(id)

    @classmethod
    def set_role(cls, role):
        bpy.context.scene.BIMOwnerProperties.active_role_id = role.id()

    @classmethod
    def import_role_attributes(cls):
        role = cls.get_role()
        props = bpy.context.scene.BIMOwnerProperties
        props.role_attributes.clear()
        blenderbim.bim.helper.import_attributes("IfcActorRole", props.role_attributes, role.get_info())

    @classmethod
    def clear_role(cls):
        bpy.context.scene.BIMOwnerProperties.active_role_id = 0

    @classmethod
    def get_role(cls):
        return tool.Ifc().get().by_id(bpy.context.scene.BIMOwnerProperties.active_role_id)

    @classmethod
    def export_role_attributes(cls):
        return blenderbim.bim.helper.export_attributes(bpy.context.scene.BIMOwnerProperties.role_attributes)

    @classmethod
    def set_actor(cls, actor):
        bpy.context.scene.BIMOwnerProperties.active_actor_id = actor.id()

    @classmethod
    def import_actor_attributes(cls, actor):
        props = bpy.context.scene.BIMOwnerProperties
        props.actor_attributes.clear()
        blenderbim.bim.helper.import_attributes2(actor, props.actor_attributes)

    @classmethod
    def clear_actor(cls):
        bpy.context.scene.BIMOwnerProperties.active_actor_id = 0

    @classmethod
    def export_actor_attributes(cls):
        props = bpy.context.scene.BIMOwnerProperties
        attributes = blenderbim.bim.helper.export_attributes(props.actor_attributes)
        return attributes

    @classmethod
    def get_actor(cls):
        return tool.Ifc().get().by_id(bpy.context.scene.BIMOwnerProperties.active_actor_id)
