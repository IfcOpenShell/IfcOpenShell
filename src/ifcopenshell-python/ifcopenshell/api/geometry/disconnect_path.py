# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell.api
import ifcopenshell.util.element
from typing import Optional


def disconnect_path(
    file: ifcopenshell.file,
    element: Optional[ifcopenshell.entity_instance] = None,
    connection_type: Optional[str] = None,
    relating_element: Optional[ifcopenshell.entity_instance] = None,
    related_element: Optional[ifcopenshell.entity_instance] = None,
) -> None:
    """There are two options to use this API method:
    - provide `element` (connected from) and `connection_type` that should be disconnected.
    - provide connected elements to disconnect explicitly:
    `relating_element` (connected from) and `related_element` (connected to)
    """
    if connection_type and element:
        connections = [
            r
            for r in element.ConnectedTo
            if r.is_a("IfcRelConnectsPathElements") and r.RelatingConnectionType == connection_type
        ] + [
            r
            for r in element.ConnectedFrom
            if r.is_a("IfcRelConnectsPathElements") and r.RelatedConnectionType == connection_type
        ]
    elif related_element:
        connections = [
            r
            for r in relating_element.ConnectedTo
            if r.is_a("IfcRelConnectsPathElements") and r.RelatedElement == related_element
        ]

    for connection in set(connections):
        history = connection.OwnerHistory
        file.remove(connection)
        if history:
            ifcopenshell.util.element.remove_deep2(file, history)
