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


def add_reference(file: ifcopenshell.file, library: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
    """Adds a new reference to a library

    A library represents an external data source, such as a database,
    spreadsheet, API, or something else that contains information related to
    the IFC project. Within a library, there will be one or more references,
    such as reference to a particular table or row in a database, or a sheet
    and row or column in a spreadsheet, a URI in a linked data Brickschema
    file, 32-bit decimal BACnetObjectIdentifier in a BACnet system, IP
    address in a network, and so on.

    These references can then be related to IFC elements. You cannot relate
    an IFC element directly to a library, it must be related to one of the
    library's references.

    :param library: The IfcLibraryInformation element to add a reference to
    :type library: ifcopenshell.entity_instance
    :return: The newly created IfcLibraryReference element
    :rtype: ifcopenshell.entity_instance

    Example:

    .. code:: python

        library = ifcopenshell.api.library.add_library(model, name="Brickschema")

        # Let's create a reference to a single AHU in our Brickschema dataset
        reference = ifcopenshell.api.library.add_reference(model, library=library)
        ifcopenshell.api.library.edit_reference(model,
            reference=reference, attributes={"Identification": "http://example.org/digitaltwin#AHU01"})
    """
    settings = {
        "library": library,
    }

    if file.schema == "IFC2X3":
        reference = file.createIfcLibraryReference()
        references = list(settings["library"].LibraryReference or [])
        references.append(reference)
        settings["library"].LibraryReference = references
        return reference
    return file.createIfcLibraryReference(ReferencedLibrary=settings["library"])
