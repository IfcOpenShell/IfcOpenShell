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
import ifcopenshell.util.element


def disconnect_element(
    file: ifcopenshell.file,
    relating_element: ifcopenshell.entity_instance,
    related_element: ifcopenshell.entity_instance,
) -> None:
    # TODO: arguments relating_element, related_element probably
    # should be renamed to element1, element2
    # as api call doesn't really treat them as "relating" and "related"
    # and just purging all connections between them
    incompatible_connections = []

    for rel in relating_element.ConnectedTo:
        if rel.is_a() == "IfcRelConnectsElements" and rel.RelatedElement == related_element:
            incompatible_connections.append(rel)

    for rel in relating_element.ConnectedFrom:
        if rel.is_a() == "IfcRelConnectsElements" and rel.RelatingElement == related_element:
            incompatible_connections.append(rel)

    for rel in related_element.ConnectedTo:
        if rel.is_a() == "IfcRelConnectsElements" and rel.RelatedElement == relating_element:
            incompatible_connections.append(rel)

    for rel in related_element.ConnectedFrom:
        if rel.is_a() == "IfcRelConnectsElements" and rel.RelatingElement == relating_element:
            incompatible_connections.append(rel)

    if incompatible_connections:
        for connection in set(incompatible_connections):
            history = connection.OwnerHistory
            file.remove(connection)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)
