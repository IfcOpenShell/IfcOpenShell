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
import ifcopenshell
from typing import Any


def edit_address(file: ifcopenshell.file, address: ifcopenshell.entity_instance, attributes: dict[str, Any]) -> None:
    """Edits the attributes of an IfcAddress

    For more information about the attributes and data types of an
    IfcAddress, consult the IFC documentation.

    :param address: The IfcAddress entity you want to edit
    :type address: ifcopenshell.entity_instance
    :param attributes: a dictionary of attribute names and values.
    :type attributes: dict
    :return: None
    :rtype: None

    Example:

    .. code:: python

        # A snail mail address
        postal = ifcopenshell.api.owner.add_address(model,
            assigned_object=organisation, ifc_class="IfcPostalAddress")
        ifcopenshell.api.owner.edit_address(model, address=postal,
            attributes={"Purpose": "OFFICE", "AddressLines": ["42 Wallaby Way"],
            "Town": "Sydney", "Region": "NSW", "PostalCode": "2000"})

        # A phone or internet address
        telecom = ifcopenshell.api.owner.add_address(model,
            assigned_object=organisation, ifc_class="IfcTelecomAddress")
        ifcopenshell.api.owner.edit_address(model, address=telecom,
            attributes={"Purpose": "OFFICE", "TelephoneNumbers": ["+61432466949"],
            "ElectronicMailAddresses": ["bobthebuilder@example.com"],
            "WWWHomePageURL": "https://thinkmoult.com"})
    """
    settings = {"address": address, "attributes": attributes}

    for name, value in settings["attributes"].items():
        setattr(settings["address"], name, value)
