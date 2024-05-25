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


def edit_information(
    file: ifcopenshell.file,
    information: ifcopenshell.entity_instance,
    attributes: dict[str, Any],
) -> None:
    """Edits the attributes of an IfcDocumentInformation

    For more information about the attributes and data types of an
    IfcDocumentInformation, consult the IFC documentation.

    :param reference: The IfcDocumentInformation entity you want to edit
    :type reference: ifcopenshell.entity_instance
    :param attributes: a dictionary of attribute names and values.
    :type attributes: dict
    :return: None
    :rtype: None

    Example:

    .. code:: python

        document = ifcopenshell.api.run("document.add_information", model)
        ifcopenshell.api.run("document.edit_information", model,
            information=document,
            attributes={"Identification": "A-GA-6100", "Name": "Overall Plan",
            "Location": "A-GA-6100 - Overall Plan.pdf"})
    """
    settings = {"information": information, "attributes": attributes}

    for name, value in settings["attributes"].items():
        setattr(settings["information"], name, value)
