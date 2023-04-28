# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.


class Usecase:
    def __init__(self, file, assigned_object=None, ifc_class="IfcPostalAddress"):
        """Add a new telecom or postal address to an organisation or person

        A person or organisation may have associated contact details such as
        phone numbers, mailing addresses, websites, email addresses, and instant
        messaging handles. This information is critical in recording the contact
        information of manufacturers and suppliers for facility management, or
        liable actors.

        There are two types of addresses, postal addresses for physical snail
        mail, and telecom addresses for telephone or internet contact numbers
        and addresses.

        :param assigned_object: The IfcOrganization or IfcPerson the contact
            address belongs to.
        :type assigned_object: ifcopenshell.entity_instance.entity_instance
        :param ifc_class: Either IfcPostalAddress or IfcTelecomAddress. Defaults
            to IfcPostalAddress.
        :type ifc_class: str, optional
        :return: The new IfcPostalAddress or IfcTelecomAddress
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            organisation = ifcopenshell.api.run("owner.add_organisation", model)

            # A snail mail address
            postal = ifcopenshell.api.run("owner.add_address", model,
                assigned_object=organisation, ifc_class="IfcPostalAddress")
            ifcopenshell.api.run("owner.edit_address", model, address=postal,
                attributes={"Purpose": "OFFICE", "AddressLines": ["42 Wallaby Way"],
                "Town": "Sydney", "Region": "NSW", "PostalCode": "2000"})

            # A phone or internet address
            telecom = ifcopenshell.api.run("owner.add_address", model,
                assigned_object=organisation, ifc_class="IfcTelecomAddress")
            ifcopenshell.api.run("owner.edit_address", model, address=telecom,
                attributes={"Purpose": "OFFICE", "TelephoneNumbers": ["+61432466949"],
                "ElectronicMailAddresses": ["bobthebuilder@example.com"],
                "WWWHomePageURL": "https://thinkmoult.com"})
        """
        self.file = file
        self.settings = {"assigned_object": assigned_object, "ifc_class": ifc_class}

    def execute(self):
        address = self.file.create_entity(self.settings["ifc_class"], "OFFICE")
        addresses = (
            list(self.settings["assigned_object"].Addresses) if self.settings["assigned_object"].Addresses else []
        )
        addresses.append(address)
        self.settings["assigned_object"].Addresses = addresses
        return address
