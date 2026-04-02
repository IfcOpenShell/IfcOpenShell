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

import json
from typing import Optional, Sequence

import ifcopenshell.api.pset
import ifcopenshell.util.element
import ifcopenshell.util.unit
from ifcopenshell.util.data import Clipping


def clip_solid(
    file: ifcopenshell.file,
    item: ifcopenshell.entity_instance,
    location: Sequence[float],
    normal: Sequence[float],
    element: Optional[ifcopenshell.entity_instance] = None,
) -> ifcopenshell.entity_instance:
    """Clip a solid with a half-space plane, returning an IfcBooleanClippingResult.

    Convenience wrapper around :class:`ifcopenshell.util.data.Clipping` for
    use with any solid.  This is the same convention used by the ``clippings``
    parameter of :func:`add_wall_representation`.

    .. warning::

        The ``normal`` points toward the **removed** material (the discarded
        side), not toward the kept material.  For a slope clip the normal
        points upward into the removed wedge above the slope line.  For a
        side mitre the normal points outward away from the wall body.

    After clipping, set the parent ``IfcShapeRepresentation``
    ``RepresentationType`` to ``"Clipping"``.

    Example — trim an extruded solid to a lean-to slope (removed material is
    above the slope)::

        bcr = ifcopenshell.api.run(
            "geometry.clip_solid", model,
            item=extrusion,
            location=[0.0, 0.0, 3.26],
            normal=[0.419, 0.0, 0.908],  # points UP toward removed material
        )

    :param item: The solid to clip (``IfcSweptAreaSolid``, ``IfcSweptDiskSolid``,
        or ``IfcBooleanClippingResult``).
    :param location: A point on the clipping plane in the representation's
        local coordinate system.
    :param normal: Plane normal pointing toward the material to be removed
        (see warning above).
    :param element: If provided, the resulting ``IfcBooleanClippingResult`` is
        registered in the element's ``BBIM_Boolean`` property set so that
        :func:`regenerate_wall_representation` preserves it during regeneration.
    :return: The resulting ``IfcBooleanClippingResult``.
    """
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)
    clipping = Clipping(location=tuple(location), normal=tuple(normal))
    result = clipping.apply(file, item, unit_scale)
    if element is not None:
        pset_data = ifcopenshell.util.element.get_pset(element, "BBIM_Boolean")
        if pset_data:
            pset = file.by_id(pset_data["id"])
            data = list(set(json.loads(pset_data["Data"]) + [result.id()]))
        else:
            pset = ifcopenshell.api.pset.add_pset(file, product=element, name="BBIM_Boolean")
            data = [result.id()]
        ifcopenshell.api.pset.edit_pset(file, pset=pset, properties={"Data": json.dumps(data)})
    return result
