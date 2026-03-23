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

import numpy as np

import ifcopenshell.api.pset
import ifcopenshell.util.element
import ifcopenshell.util.unit
from ifcopenshell.util.shape_builder import ShapeBuilder


def clip_solid_bounded(
    file: ifcopenshell.file,
    item: ifcopenshell.entity_instance,
    location: Sequence[float],
    normal: Sequence[float],
    boundary_points: Sequence[Sequence[float]],
    boundary_position: Sequence[float] = (0.0, 0.0, 0.0),
    element: Optional[ifcopenshell.entity_instance] = None,
) -> ifcopenshell.entity_instance:
    """Clip a solid with a polygonally bounded half-space, returning an IfcBooleanClippingResult.

    Like :func:`clip_solid`, but the boolean subtraction is restricted to the
    region enclosed by ``boundary_points`` rather than extending across the
    entire half-space.  The clipping plane is still infinite, but material is
    only removed within the extruded footprint of the polygon.

    The ``normal`` convention is the same as :func:`clip_solid`: it points
    toward the **removed** material.

    After clipping, set the parent ``IfcShapeRepresentation``
    ``RepresentationType`` to ``"Clipping"``.

    Example::

        bcr = ifcopenshell.api.run(
            "geometry.clip_solid_bounded", model,
            item=extrusion,
            location=[2.5, 0.0, 2.0],
            normal=[0.6, 0.0, 0.8],
            boundary_points=[[2.0, 0.0], [3.0, 0.0], [3.0, 2.0], [2.0, 2.0]],
        )

    :param item: The solid to clip (``IfcSweptAreaSolid``, ``IfcSweptDiskSolid``,
        or ``IfcBooleanClippingResult``).
    :param location: A point on the clipping plane in the representation's
        local coordinate system.
    :param normal: Plane normal pointing toward the material to be removed.
    :param boundary_points: 2D ``[x, y]`` points defining the closed polygonal
        boundary in the coordinate system of ``boundary_position``.  The polygon
        is automatically closed — do not repeat the first point.
    :param boundary_position: 3D origin of the boundary coordinate system
        (axes default to the global X/Y/Z directions).  Defaults to the origin.
    :param element: If provided, the resulting ``IfcBooleanClippingResult`` is
        registered in the element's ``BBIM_Boolean`` property set so that
        :func:`regenerate_wall_representation` preserves it during regeneration.
    :return: The resulting ``IfcBooleanClippingResult``.
    """
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(file)
    builder = ShapeBuilder(file)

    normal_arr = np.array(normal)
    if np.allclose(normal_arr, [0.0, 0.0, 1.0], atol=1e-2) or np.allclose(normal_arr, [0.0, 0.0, -1.0], atol=1e-2):
        arbitrary_vector = np.array([0.0, 1.0, 0.0])
    else:
        arbitrary_vector = np.array([0.0, 0.0, 1.0])
    x_axis = np.cross(normal_arr, arbitrary_vector)
    x_axis /= np.linalg.norm(x_axis)

    scaled_location = [i / unit_scale for i in location]
    plane_placement = builder.create_axis2_placement_3d(scaled_location, normal, x_axis)
    plane = file.create_entity("IfcPlane", plane_placement)

    scaled_boundary_position = [i / unit_scale for i in boundary_position]
    boundary_pos_entity = file.create_entity(
        "IfcAxis2Placement3D",
        file.create_entity("IfcCartesianPoint", scaled_boundary_position),
    )

    scaled_pts = [[p[0] / unit_scale, p[1] / unit_scale] for p in boundary_points]
    scaled_pts.append(scaled_pts[0])  # close the polygon
    ifc_pts = [file.create_entity("IfcCartesianPoint", p) for p in scaled_pts]
    boundary = file.createIfcPolyline(ifc_pts)

    half_space = file.create_entity("IfcPolygonalBoundedHalfSpace", plane, False, boundary_pos_entity, boundary)
    result = file.create_entity("IfcBooleanClippingResult", "DIFFERENCE", item, half_space)
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
