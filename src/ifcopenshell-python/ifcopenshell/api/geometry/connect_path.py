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
import ifcopenshell.api.owner
import ifcopenshell.guid
import ifcopenshell.util.element
from typing import Optional


def connect_path(
    file: ifcopenshell.file,
    relating_element: ifcopenshell.entity_instance,
    related_element: ifcopenshell.entity_instance,
    relating_connection: str = "NOTDEFINED",
    related_connection: str = "NOTDEFINED",
    description: Optional[str] = None,
) -> ifcopenshell.entity_instance:
    incompatible_connections: list[ifcopenshell.entity_instance] = []
    for rel in relating_element.ConnectedTo:
        if not rel.is_a("IfcRelConnectsPathElements"):
            continue
        if rel.RelatedElement == related_element:
            incompatible_connections.append(rel)
        elif rel.RelatingConnectionType in ["ATSTART", "ATEND"] and rel.RelatingConnectionType == relating_connection:
            incompatible_connections.append(rel)

    for rel in relating_element.ConnectedFrom:
        if not rel.is_a("IfcRelConnectsPathElements"):
            continue
        if rel.RelatedConnectionType in ["ATSTART", "ATEND"] and rel.RelatedConnectionType == relating_connection:
            incompatible_connections.append(rel)

    for rel in related_element.ConnectedFrom:
        if not rel.is_a("IfcRelConnectsPathElements"):
            continue
        if rel.RelatedConnectionType in ["ATSTART", "ATEND"] and rel.RelatedConnectionType == related_connection:
            incompatible_connections.append(rel)

    for rel in related_element.ConnectedTo:
        if not rel.is_a("IfcRelConnectsPathElements"):
            continue
        if rel.RelatedElement == relating_element:
            incompatible_connections.append(rel)
        elif rel.RelatingConnectionType in ["ATSTART", "ATEND"] and rel.RelatingConnectionType == related_connection:
            incompatible_connections.append(rel)

    if incompatible_connections:
        for connection in set(incompatible_connections):
            history = connection.OwnerHistory
            file.remove(connection)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)

    return file.create_entity(
        "IfcRelConnectsPathElements",
        ifcopenshell.guid.new(),
        OwnerHistory=ifcopenshell.api.owner.create_owner_history(file),
        Description=description,
        RelatingElement=relating_element,
        RelatedElement=related_element,
        RelatingConnectionType=relating_connection,
        RelatedConnectionType=related_connection,
        RelatingPriorities=[],
        RelatedPriorities=[],
    )
