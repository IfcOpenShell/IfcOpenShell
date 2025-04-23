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
from typing import Optional


def remove_structural_boundary_condition(
    file: ifcopenshell.file,
    connection: Optional[ifcopenshell.entity_instance] = None,
    boundary_condition: Optional[ifcopenshell.entity_instance] = None,
) -> None:
    """Removes a condition from a connection, or an orphaned boundary condition

    :param connection: The IfcStructuralConnection to remove the condition
        from. If omitted, it is assumed to be an orphaned condition.
    :param boundary_condition: The IfcBoundaryCondition to remove.
    :return: None
    """

    if connection:
        # remove boundary condition from a connection
        if not connection.AppliedCondition:
            return
        applied_condition = connection.AppliedCondition
        if file.get_total_inverses(applied_condition) == 1:
            file.remove(applied_condition)
        connection.AppliedCondition = None
    else:
        assert boundary_condition, "Either connection or boundary_condition must be provided."
        # remove the boundary condition
        for conn in file.get_inverse(boundary_condition):
            conn.AppliedCondition = None
        file.remove(boundary_condition)
