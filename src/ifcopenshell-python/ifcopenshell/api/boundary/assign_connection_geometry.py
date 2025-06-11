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

import ifcopenshell.util.unit
import numpy as np
import numpy.typing as npt
from typing import Optional
from ifcopenshell.util.shape_builder import SequenceOfVectors, V, ifc_safe_vector_type


def assign_connection_geometry(
    file: ifcopenshell.file,
    rel_space_boundary: ifcopenshell.entity_instance,
    outer_boundary: SequenceOfVectors,
    location: tuple[float, float, float],
    axis: tuple[float, float, float],
    ref_direction: tuple[float, float, float],
    inner_boundaries: Optional[SequenceOfVectors] = None,
    unit_scale: Optional[float] = None,
) -> None:
    """Create and assign a connection geometry to a space boundary relationship

    A space boundary may optionally have a plane that represents how that
    space is adjacent to another space, known as the connection geometry.
    You may specify this plane in terms of an outer boundary polyline, zero
    or more inner boundaries (such as for windows), and a positional matrix
    for the orientation of the plane.

    :param rel_space_boundary: The space boundary relationship to assign the
        connection geometry to.
    :param outer_boundary: A list of 2D points representing an open
        polyline.  The last point will connect to the first point. Each
        point is represented by an interable of 2 floats. The coordinates of
        the points are relative to the positional matrix arguments.
    :param inner_boundaries: A list of zero or more inner boundaries to use
        for the plane. Each boundary is represented by an open polyline, as
        defined by the outer_boundary argument.
    :param location: The local origin of the connection geometry, defined as
        an XYZ coordinate relative to the placement of the space that is
        being bounded.
    :param axis: The local X axis of the connection geometry, defined as an
        XYZ vector relative to the placement of the space that is being
        bounded.
    :param ref_direction: The local Z axis of the connection geometry,
        defined as an XYZ vector relative to the placement of the space that
        is being bounded. The Y vector is automatically derived using the
        right hand rule.
    :param unit_scale: The unit scale as calculated by
        ifcopenshell.util.unit.calculate_unit_scale. If not provided, it
        will be automatically calculated for you.
    :type unit_scale: float, optional
    :return: None

    Example:

    .. code:: python

        ifcopenshell.api.boundary.assign_connection_geometry(model,
            rel_space_boundary=element,
            outer_boundary=[(0., 0.), (1., 0.), (1., 1.), (0., 1.)],
            location=[0., 0., 0.], axis=[1., 0., 0.], ref_direction=[0., 0., 1.],
            )
    """
    usecase = Usecase()
    usecase.file = file
    usecase.rel_space_boundary = rel_space_boundary
    usecase.outer_boundary = V(outer_boundary)
    usecase.inner_boundaries = V(inner_boundaries or [])
    usecase.location = V(location)
    usecase.axis = V(axis)
    usecase.ref_direction = V(ref_direction)
    usecase.unit_scale = unit_scale if unit_scale is not None else ifcopenshell.util.unit.calculate_unit_scale(file)
    return usecase.execute()


class Usecase:
    file: ifcopenshell.file
    rel_space_boundary: ifcopenshell.entity_instance
    outer_boundary: npt.NDArray
    inner_boundaries: npt.NDArray
    location: npt.NDArray
    axis: npt.NDArray
    ref_direction: npt.NDArray
    unit_scale: float

    def execute(self):
        outer_boundary = self.create_polyline(self.outer_boundary)
        inner_boundaries = tuple(self.create_polyline(boundary) for boundary in self.inner_boundaries)
        plane = self.create_plane(self.location, self.axis, self.ref_direction)
        curve_bounded_plane = self.file.createIfcCurveBoundedPlane(plane, outer_boundary, inner_boundaries)
        connection_geometry = self.file.createIfcConnectionSurfaceGeometry(curve_bounded_plane)
        self.rel_space_boundary.ConnectionGeometry = connection_geometry

    def create_point(self, point: npt.NDArray) -> ifcopenshell.entity_instance:
        return self.file.create_enitty("IfcCartesianPoint", ifc_safe_vector_type(point / self.unit_scale))

    def close_polyline(
        self, points: tuple[ifcopenshell.entity_instance, ...]
    ) -> tuple[ifcopenshell.entity_instance, ...]:
        return points + (points[0],)

    def create_polyline(self, points: npt.NDArray) -> ifcopenshell.entity_instance:
        if np.allclose(points[0], points[-1]):
            points = points[0 : len(points) - 1]
        ifc_points = tuple(self.create_point(point) for point in points)
        return self.file.createIfcPolyline(self.close_polyline(ifc_points))

    def create_plane(
        self, location: npt.NDArray, axis: npt.NDArray, ref_direction: npt.NDArray
    ) -> ifcopenshell.entity_instance:
        return self.file.createIfcPlane(
            self.file.createIfcAxis2Placement3D(
                self.create_point(location),
                self.file.createIfcDirection(axis),
                self.file.createIfcDirection(ref_direction),
            )
        )
