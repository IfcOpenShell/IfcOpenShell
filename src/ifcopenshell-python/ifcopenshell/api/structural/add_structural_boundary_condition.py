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
from typing import Optional

import ifcopenshell
import ifcopenshell.util.attribute


def _initialize_stiffnesses_to_free(file: ifcopenshell.file, condition: ifcopenshell.entity_instance) -> None:
    for i in range(1, len(condition)):
        attr_decl = condition.declaration.all_attributes()[i]
        attr_name = condition.attribute_name(i)
        named = attr_decl.type_of_attribute().as_named_type()
        if named and named.declared_type().as_select_type():
            select_items = [s.name() for s in ifcopenshell.util.attribute.get_select_items(attr_decl)]
            if "IfcBoolean" in select_items:
                setattr(condition, attr_name, file.createIfcBoolean(False))
        elif file.schema == "IFC2X3":
            setattr(condition, attr_name, 0.0)


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
    :param connection: The IfcStructuralConnection to apply the boundary
        condition to. This will determine the type of condition that is
        created. If no connection is supplied, an orphan boundary condition
        will be created using the ifc_class that you specify.
    :param ifc_class: The class of IfcBoundaryCondition to create, only
        relevant if you do not specify a connection and want to create an
        orphaned boundary condition.
    :return: The newly created IfcBoundaryCondition

    Example:

    .. code:: python

        ifcopenshell.api.structural.add_structural_boundary_condition(model, connection=connection)
    """
    if connection:
        # assign boundary condition to a connection
        if connection.is_a("IfcRelConnectsStructuralMember"):
            related_connection = connection.RelatedStructuralConnection
        else:
            related_connection = connection

        if related_connection.is_a("IfcStructuralPointConnection"):
            boundary_class = "IfcBoundaryNodeCondition"
        elif related_connection.is_a("IfcStructuralCurveConnection"):
            boundary_class = "IfcBoundaryEdgeCondition"
        elif related_connection.is_a("IfcStructuralSurfaceConnection"):
            boundary_class = "IfcBoundaryFaceCondition"
        else:
            assert False, related_connection

        condition = file.create_entity(boundary_class, Name=name)
        _initialize_stiffnesses_to_free(file, condition)
        connection.AppliedCondition = condition
        return condition
    else:
        # add an orphan boundary condition
        condition = file.create_entity(ifc_class, Name=name)
        _initialize_stiffnesses_to_free(file, condition)
        return condition
