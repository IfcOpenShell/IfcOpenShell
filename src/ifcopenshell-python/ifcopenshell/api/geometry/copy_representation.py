# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

from __future__ import annotations

from typing import Optional

import ifcopenshell.api.geometry
import ifcopenshell.util.element
import ifcopenshell.util.representation


def copy_representation(
    file: ifcopenshell.file,
    source: ifcopenshell.entity_instance,
    target: ifcopenshell.entity_instance,
    context_identifier: str = "Body",
) -> Optional[ifcopenshell.entity_instance]:
    """Copy a geometric representation from one element to another.

    Finds the named representation on ``source``, deep-copies its entity
    graph (geometry items, profiles, placements, etc.), and assigns the copy
    to ``target``.  Representation contexts are shared rather than copied.
    If ``target`` already has a matching representation it is removed and
    replaced.

    If no matching representation is found on ``source``, returns ``None``
    and leaves ``target`` unchanged.

    :param source: The element to copy the representation from.
    :param target: The element to assign the copied representation to.
    :param context_identifier: The RepresentationIdentifier to look up on
        ``source`` (e.g. ``"Body"``, ``"Axis"``, ``"Box"``).
        Defaults to ``"Body"``.
    :return: The newly created IfcShapeRepresentation, or None if no
        matching representation was found on ``source``.

    Example:

    .. code:: python

        wall_a = model.by_id(1)
        wall_b = model.by_id(2)

        # Give wall_b the same body geometry as wall_a.
        ifcopenshell.api.geometry.copy_representation(model,
            source=wall_a, target=wall_b)
    """
    source_rep = ifcopenshell.util.representation.get_representation(source, "Model", context_identifier)
    if source_rep is None:
        return None

    new_rep = ifcopenshell.util.element.copy_deep(file, source_rep, exclude=["IfcGeometricRepresentationContext"])

    existing_rep = ifcopenshell.util.representation.get_representation(target, "Model", context_identifier)
    if existing_rep:
        ifcopenshell.api.geometry.unassign_representation(file, product=target, representation=existing_rep)
        ifcopenshell.api.geometry.remove_representation(file, representation=existing_rep)

    ifcopenshell.api.geometry.assign_representation(file, product=target, representation=new_rep)
    return new_rep
