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


def add_structural_boundary_condition(
    file: ifcopenshell.file,
    name: Optional[str] = None,
    connection: Optional[ifcopenshell.entity_instance] = None,
    ifc_class: str = "IfcBoundaryNodeCondition",
) -> ifcopenshell.entity_instance:
    """Adds a new structural boundary condition to a structural connection

    The type of boundary condition depends on the connection. Point
    connections will have a node condition, curve connections will have an
    edge condition, and surface connections will have a face condition.

    :param name: The name of the boundary condition.
    :type name: str,optional
    :param connection: The IfcStructuralConnection to apply the boundary
        condition to. This will determine the type of condition that is
        created. If no connection is supplied, an orphan boundary condition
        will be created using the ifc_class that you specify.
    :type connection: ifcopenshell.entity_instance,optional
    :param ifc_class: The class of IfcBoundaryCondition to create, only
        relevant if you do not specify a connection and want to create an
        orphaned boundary condition.
    :type ifc_class: str,optional
    :return: The newly created IfcBoundaryCondition
    :rtype: ifcopenshell.entity_instance

    Example:

    .. code:: python

        ifcopenshell.api.structural.add_structural_boundary_condition(model, connection=connection)
    """
    settings = {"name": name, "connection": connection, "ifc_class": ifc_class}

    if settings["connection"]:
        # assign boundary condition to a connection
        if settings["connection"].is_a("IfcRelConnectsStructuralMember"):
            related_connection = settings["connection"].RelatedStructuralConnection
        else:
            related_connection = settings["connection"]

        if related_connection.is_a("IfcStructuralPointConnection"):
            boundary_class = "IfcBoundaryNodeCondition"
        elif related_connection.is_a("IfcStructuralCurveConnection"):
            boundary_class = "IfcBoundaryEdgeCondition"
        elif related_connection.is_a("IfcStructuralSurfaceConnection"):
            boundary_class = "IfcBoundaryFaceCondition"

        condition = file.create_entity(boundary_class, Name=settings["name"])
        settings["connection"].AppliedCondition = condition
        return condition
    else:
        # add an orphan boundary condition
        return file.create_entity(settings["ifc_class"], Name=settings["name"])
