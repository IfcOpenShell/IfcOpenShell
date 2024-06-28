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
    settings = {
        "relating_element": relating_element,
        "related_element": related_element,
        "relating_connection": relating_connection,
        "related_connection": related_connection,
        "description": description,
    }

    incompatible_connections = []
    for rel in settings["relating_element"].ConnectedTo:
        if not rel.is_a("IfcRelConnectsPathElements"):
            continue
        if rel.RelatedElement == settings["related_element"]:
            incompatible_connections.append(rel)
        elif (
            rel.RelatingConnectionType in ["ATSTART", "ATEND"]
            and rel.RelatingConnectionType == settings["relating_connection"]
        ):
            incompatible_connections.append(rel)

    for rel in settings["relating_element"].ConnectedFrom:
        if not rel.is_a("IfcRelConnectsPathElements"):
            continue
        if (
            rel.RelatedConnectionType in ["ATSTART", "ATEND"]
            and rel.RelatedConnectionType == settings["relating_connection"]
        ):
            incompatible_connections.append(rel)

    for rel in settings["related_element"].ConnectedFrom:
        if not rel.is_a("IfcRelConnectsPathElements"):
            continue
        if (
            rel.RelatedConnectionType in ["ATSTART", "ATEND"]
            and rel.RelatedConnectionType == settings["related_connection"]
        ):
            incompatible_connections.append(rel)

    for rel in settings["related_element"].ConnectedTo:
        if not rel.is_a("IfcRelConnectsPathElements"):
            continue
        if rel.RelatedElement == settings["relating_element"]:
            incompatible_connections.append(rel)
        elif (
            rel.RelatingConnectionType in ["ATSTART", "ATEND"]
            and rel.RelatingConnectionType == settings["related_connection"]
        ):
            incompatible_connections.append(rel)

    if incompatible_connections:
        for connection in set(incompatible_connections):
            history = connection.OwnerHistory
            file.remove(connection)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)

    return file.createIfcRelConnectsPathElements(
        ifcopenshell.guid.new(),
        OwnerHistory=ifcopenshell.api.owner.create_owner_history(file),
        Description=settings["description"],
        RelatingElement=settings["relating_element"],
        RelatedElement=settings["related_element"],
        RelatingConnectionType=settings["relating_connection"],
        RelatedConnectionType=settings["related_connection"],
        RelatingPriorities=[],
        RelatedPriorities=[],
    )
