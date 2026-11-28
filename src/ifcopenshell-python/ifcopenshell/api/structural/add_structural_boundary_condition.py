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
from typing import Literal, Optional

import ifcopenshell
import ifcopenshell.util.attribute
import ifcopenshell.util.structural


def _is_translational(name: str) -> bool:
    # IFC4 calls them TranslationalStiffness*, IFC2X3 LinearStiffness*.
    return name.startswith("Translational") or name.startswith("Linear")


def _get_held_stiffnesses(
    file: ifcopenshell.file, ifc_class: str, support: Literal["FREE", "PINNED", "FIXED"]
) -> list[str]:
    """The stiffness attributes to set to True, checking that the schema can say a stiffness is rigid"""
    if support == "FREE":
        return []
    if support not in ("PINNED", "FIXED"):
        raise ValueError(f"Unknown support {support}: choose from FREE, PINNED or FIXED")
    held = []
    for attribute in (
        ifcopenshell.schema_by_name(file.schema_identifier).declaration_by_name(ifc_class).as_entity().all_attributes()
    ):
        name = attribute.name()
        if not (_is_translational(name) or (support == "FIXED" and name.startswith("Rotational"))):
            continue
        named = attribute.type_of_attribute().as_named_type()
        if not (named and named.declared_type().as_select_type()) or "IfcBoolean" not in [
            s.name() for s in ifcopenshell.util.attribute.get_select_items(attribute)
        ]:
            raise ValueError(f"{ifc_class} cannot say that a stiffness is rigid in {file.schema}")
        held.append(name)
    return held


def _initialize_stiffnesses(file: ifcopenshell.file, condition: ifcopenshell.entity_instance, held: list[str]) -> None:
    for i in range(1, len(condition)):
        attr_decl = condition.declaration.all_attributes()[i]
        attr_name = condition.attribute_name(i)
        named = attr_decl.type_of_attribute().as_named_type()
        if named and named.declared_type().as_select_type():
            select_items = [s.name() for s in ifcopenshell.util.attribute.get_select_items(attr_decl)]
            if "IfcBoolean" in select_items:
                setattr(condition, attr_name, file.createIfcBoolean(attr_name in held))
        elif file.schema == "IFC2X3":
            setattr(condition, attr_name, 0.0)


def add_structural_boundary_condition(
    file: ifcopenshell.file,
    name: Optional[str] = None,
    connection: Optional[ifcopenshell.entity_instance] = None,
    ifc_class: str = "IfcBoundaryNodeCondition",
    support: Literal["FREE", "PINNED", "FIXED"] = "FREE",
) -> ifcopenshell.entity_instance:
    """Adds a new structural boundary condition to a structural connection

    The type of boundary condition depends on the connection. Point
    connections will have a node condition, curve connections will have an
    edge condition, and surface connections will have a face condition.

    The condition is free by default: every stiffness is False (0.0 in
    IFC2X3). A PINNED condition holds every displacement and leaves the
    rotations free; a FIXED one holds the rotations as well. A face
    condition has displacements only, so the two are the same for it. A
    warping stiffness is left free. Use
    :func:`edit_structural_boundary_condition` for any other condition.

    :param name: The name of the boundary condition.
    :param connection: The IfcStructuralConnection to apply the boundary
        condition to. This will determine the type of condition that is
        created. If no connection is supplied, an orphan boundary condition
        will be created using the ifc_class that you specify.
    :param ifc_class: The class of IfcBoundaryCondition to create, only
        relevant if you do not specify a connection and want to create an
        orphaned boundary condition.
    :param support: FREE, PINNED or FIXED.
    :raises ValueError: if the condition is PINNED or FIXED and the schema
        cannot say that a stiffness is rigid, as in IFC2X3, where stiffnesses
        are numbers only. Nothing is created.
    :return: The newly created IfcBoundaryCondition

    Example:

    .. code:: python

        connection = ifcopenshell.api.root.create_entity(model, ifc_class="IfcStructuralPointConnection")
        ifcopenshell.api.structural.add_structural_boundary_condition(model, connection=connection)
        # A support that holds every displacement and rotation
        ifcopenshell.api.structural.add_structural_boundary_condition(
            model, name="Fixed", connection=connection, support="FIXED"
        )
    """
    if connection:
        # assign boundary condition to a connection
        if connection.is_a("IfcRelConnectsStructuralMember"):
            related_connection = connection.RelatedStructuralConnection
        else:
            related_connection = connection
        ifc_class = ifcopenshell.util.structural.get_boundary_condition_class(related_connection)

    held = _get_held_stiffnesses(file, ifc_class, support)
    condition = file.create_entity(ifc_class, Name=name)
    _initialize_stiffnesses(file, condition, held)
    if connection:
        connection.AppliedCondition = condition
    return condition
