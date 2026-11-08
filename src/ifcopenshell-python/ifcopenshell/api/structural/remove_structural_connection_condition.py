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
import ifcopenshell.util.element


def remove_structural_connection_condition(file: ifcopenshell.file, relation: ifcopenshell.entity_instance) -> None:
    """Removes a relationship between a member and a connection

    The relationship's own AppliedCondition (how the member is attached to
    the connection, such as a release) is removed with it unless something
    else uses it, as :func:`remove_structural_boundary_condition` does for a
    connection. The member, the connection and the connection's own
    AppliedCondition (its support) are preserved.

    :param relation: The IfcRelConnectsStructuralMember to remove.
    :return: None
    """
    if (condition := relation.AppliedCondition) and file.get_total_inverses(condition) == 1:
        file.remove(condition)
    history = relation.OwnerHistory
    file.remove(relation)
    if history:
        ifcopenshell.util.element.remove_deep2(file, history)
