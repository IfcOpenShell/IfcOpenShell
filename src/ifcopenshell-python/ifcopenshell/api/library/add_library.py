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
import ifcopenshell.util.schema
import ifcopenshell.util.date


def add_library(file: ifcopenshell.file, name: str) -> ifcopenshell.entity_instance:
    """Adds a new library to the project

    A library is an external data source that is related to the project. It
    may be a database, a spreadsheet, an API, or even a stack of papers in a
    filing cabinet. This allows IFC data to store relationships to these
    external data sources.

    For example, you may have a list of laser scans of a site stored in an
    online platform, which can be queried using an API. Or, you might have a
    database of live building sensor data. So long as there is a clear
    identifier you can use to link the two datasets together, you can create
    a relationship.

    Note that IFC does not store any instructions on how to access the
    library. It does not specify whether a HTTP request or database
    connection needs to be made or what protocol the library operates with.
    Until this is fleshed out further, it is the users responsibility to
    name the libraries consistently and use appropriate identifiers. For
    example, if you are linking IFC data and Brickschema data, use a full
    URI for the identifier with no abbreviation (e.g.
    'http://example.org/digitaltwin#AHU01', not 'digitaltwin:AHU01').

    A library will then contain a list of references within that library.
    These references will then be related to IFC elements. For example, a
    library will represent an external database, and a reference will point
    to a particular table and row within that database.

    :param name: The name of the library
    :return: The newly created IfcLibraryInformation

    Example:

    .. code:: python

        ifcopenshell.api.library.add_library(model, name="Brickschema")
    """
    return file.create_entity("IfcLibraryInformation", Name=name)
