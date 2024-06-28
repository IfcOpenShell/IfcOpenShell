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


def connect_element(
    file: ifcopenshell.file,
    relating_element: ifcopenshell.entity_instance,
    related_element: ifcopenshell.entity_instance,
    description: Optional[str] = None,
) -> ifcopenshell.entity_instance:
    settings = {
        "relating_element": relating_element,
        "related_element": related_element,
        "description": description,
    }

    incompatible_connections = []

    for rel in settings["relating_element"].ConnectedFrom:
        if rel.is_a() == "IfcRelConnectsElements" and rel.RelatingElement == settings["related_element"]:
            incompatible_connections.append(rel)

    for rel in settings["related_element"].ConnectedTo:
        if rel.is_a() == "IfcRelConnectsElements" and rel.RelatedElement == settings["relating_element"]:
            incompatible_connections.append(rel)

    if incompatible_connections:
        for connection in set(incompatible_connections):
            history = connection.OwnerHistory
            file.remove(connection)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)

    for rel in settings["relating_element"].ConnectedTo:
        if rel.is_a() == "IfcRelConnectsElements" and rel.RelatedElement == settings["related_element"]:
            rel.Description = settings["description"]
            return rel

    return file.createIfcRelConnectsElements(
        ifcopenshell.guid.new(),
        OwnerHistory=ifcopenshell.api.owner.create_owner_history(file),
        Description=settings["description"],
        RelatingElement=settings["relating_element"],
        RelatedElement=settings["related_element"],
    )
