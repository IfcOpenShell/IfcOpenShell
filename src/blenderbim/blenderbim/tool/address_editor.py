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
import blenderbim.bim.helper
import blenderbim.tool as tool


class AddressEditor(blenderbim.core.tool.AddressEditor):
    @classmethod
    def set_address(cls, address):
        bpy.context.scene.BIMOwnerProperties.active_address_id = address.id()

    @classmethod
    def import_attributes(cls):
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
    def export_attributes(cls):
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
    def add_attribute(cls, name):
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
    def remove_attribute(cls, name, id):
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
