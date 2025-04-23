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
import ifcopenshell.api.root


def add_structural_member_connection(
    file: ifcopenshell.file,
    relating_structural_member: ifcopenshell.entity_instance,
    related_structural_connection: ifcopenshell.entity_instance,
) -> ifcopenshell.entity_instance:
    """Relates a structural member and a structural connection

    :param relating_structural_member: The IfcStructuralMember to have a
        connection added to it.
    :param related_structural_connection: The IfcStructuralConnection to add
        to the IfcStructuralMember.
    :return: The IfcRelConnectsStructuralMember relationship
    """

    for connection in related_structural_connection.ConnectsStructuralMembers or []:
        if connection.RelatingStructuralMember == relating_structural_member:
            return connection
    rel = ifcopenshell.api.root.create_entity(file, ifc_class="IfcRelConnectsStructuralMember")
    rel.RelatingStructuralMember = relating_structural_member
    rel.RelatedStructuralConnection = related_structural_connection
    return rel
