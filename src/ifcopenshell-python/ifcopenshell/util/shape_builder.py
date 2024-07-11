# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022, 2023 @Andrej730
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

import numpy as np
import numpy.typing as npt
import collections
import collections.abc
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.element
import ifcopenshell.util.representation
import ifcopenshell.util.unit
from math import cos, sin, pi, tan, radians, degrees, atan, sqrt
from typing import Union, Optional, Literal, Any, Sequence
from itertools import chain
from mathutils import Vector, Matrix

V = lambda *x: Vector([float(i) for i in x])
sign = lambda x: x and (1, -1)[x < 0]
PRECISION = 1.0e-5

VectorTuple = type[tuple[float, float, float]]
"tuple of 3 `float` values"


def is_x(value, x, si_conversion=None):
    if si_conversion:
        value = value * si_conversion
    return (x + PRECISION) > value > (x - PRECISION)


round_to_precision = lambda x, si_conversion: round(x * si_conversion, 5) / si_conversion
round_vector_to_precision = lambda v, si_conversion: Vector([round_to_precision(i, si_conversion) for i in v])


# Note: using ShapeBuilder try not to reuse IFC elements in the process
# otherwise you might run into situation where builder.mirror or other operation
# is applied twice during one run to the same element
# which might produce undesirable results


class ShapeBuilder:
    def __init__(self, ifc_file: ifcopenshell.file):
        self.file = ifc_file

    def polyline(
        self,
        points: list[Vector],
        closed: bool = False,
        position_offset: Optional[Vector] = None,
        arc_points: list[int] = [],
    ) -> ifcopenshell.entity_instance:
        """
        Generate an IfcIndexedPolyCurve based on the provided points.

        :param points: List of 2d or 3d points
        :type points: list[Vector]
        :param closed: Whether polyline should be closed. Default is `False`
        :type closed: bool, optional
        :param position_offset: offset to be applied to all points
        :type position_offset: Vector, optional
        :param arc_points: Indices of the middle points for arcs. For creating an arc segment,
            provide 3 points: `arc_start`, `arc_middle` and `arc_end` to `points` and add the `arc_middle`
            point's index to `arc_points`
        :type arc_points: list[int], optional

        :return: IfcIndexedPolyCurve
        :rtype: ifcopenshell.entity_instance

        Example:

        .. code:: python

            # rectangle
            points = Vector((0, 0)), Vector((1, 0)), Vector((1, 1)), Vector((0, 1))
            position = Vector((2, 0))
            # #2=IfcIndexedPolyCurve(#1,(IfcLineIndex((1,2,3,4,1))),$)
            polyline = builder.polyline(points, closed=True, position_offset=position)

            # arc between points (1,0) and (0,1). Second point in the arc should be it's middle
            points = Vector((1, 0)), Vector((0.707, 0.707)), Vector((0, 1)), Vector((0,2))
            arc_points = (1,) # point with index 1 is a middle of the arc
            # 4=IfcIndexedPolyCurve(#3,(IfcArcIndex((1,2,3)),IfcLineIndex((3,4,1))),$)
            curved_polyline = builder.polyline(points, closed=False, position_offset=position, arc_points=arc_points)
        """

        if arc_points and self.file.schema == "IFC2X3":
            raise Exception("Arcs are not supported for IFC2X3.")

        if position_offset:
            points = [Vector(p) + position_offset for p in points]

        if self.file.schema == "IFC2X3":
            points = [self.file.createIfcCartesianPoint(p) for p in points]
            if closed:
                points.append(points[0])
            ifc_curve = self.file.createIfcPolyline(Points=points)
            return ifc_curve

        dimensions = len(points[0])
        if dimensions == 2:
            ifc_points = self.file.createIfcCartesianPointList2D(points)
        elif dimensions == 3:
            ifc_points = self.file.createIfcCartesianPointList3D(points)

        if not closed and not arc_points:
            ifc_curve = self.file.createIfcIndexedPolyCurve(Points=ifc_points)
            return ifc_curve

        # if curve is closed or we have arc points
        # then we do need to create segments
        segments = []
        cur_i = 0
        closed_by_arc = False
        while cur_i < len(points) - 1:
            cur_i_ifc = cur_i + 1
            if cur_i + 1 in arc_points:
                if cur_i_ifc + 1 < len(points):
                    segments.append((cur_i_ifc, cur_i_ifc + 1, cur_i_ifc + 2))
                else:
                    segments.append((cur_i_ifc, cur_i_ifc + 1, 1))
                    closed_by_arc = True
                cur_i += 2
            else:
                segments.append((cur_i_ifc, cur_i_ifc + 1))
                cur_i += 1

        if closed and not closed_by_arc:
            segments.append((len(points), 1))

        ifc_segments = []
        # because IfcLineIndex support 2+ points
        # we merge neighbor line segments into one
        current_line_segment = []
        last_segment = len(segments) - 1
        for seg_i, segment in enumerate(segments):
            if len(segment) == 2:
                # check if `current_line_segment` is empty to avoid duplicated indices like `IfcLineIndex((1,2,2,3,3,4,4,1))`
                current_line_segment += segment if not current_line_segment else segment[1:]

            if current_line_segment and (len(segment) == 3 or seg_i == last_segment):
                ifc_segments.append(self.file.createIfcLineIndex(current_line_segment))
                current_line_segment = []

            if len(segment) == 3:
                ifc_segments.append(self.file.createIfcArcIndex(segment))

        # NOTE: IfcIndexPolyCurve support only consecutive segments
        ifc_curve = self.file.createIfcIndexedPolyCurve(Points=ifc_points, Segments=ifc_segments)
        return ifc_curve

    def get_rectangle_coords(
        self, size: Vector = Vector((1.0, 1.0)).freeze(), position: Optional[Vector] = None
    ) -> list[Vector]:
        """
        Get rectangle coords arranged as below:

        ::

            3 2
            0 1

        :param size: rectangle size, could be either 2d or 3d, defaults to `(1,1)`
        :type size: Vector, optional
        :param position: rectangle position, default to `None`.
            if `position` not specified zero-vector will be used
        :type position: Vector, optional

        :return: list of rectangle coords
        :rtype: List[Vector]
        """
        dimensions = len(size)

        if not position:
            position = Vector([0] * dimensions)

        # adds support both 2d and 3d sizes
        non_empty_coords = [i for i, v in enumerate(size) if v]
        id_matrix = Matrix.Identity(dimensions)

        points = [
            position,
            position + size * id_matrix[non_empty_coords[0]],
            position + size,
            position + size * id_matrix[non_empty_coords[1]],
        ]
        return points

    def rectangle(
        self, size: Vector = Vector((1.0, 1.0)).freeze(), position: Vector = None
    ) -> ifcopenshell.entity_instance:
        """
        Generate a rectangle polyline.

        :param size: rectangle size, could be either 2d or 3d, defaults to `(1,1)`
        :type size: Vector, optional
        :param position: rectangle position, default to `None`.
            if `position` not specified zero-vector will be used
        :type position: Vector, optional

        :return: IfcIndexedPolyCurve
        :rtype: ifcopenshell.entity_instance
        """
        return self.polyline(self.get_rectangle_coords(size, position), closed=True)

    def circle(self, center: Vector = Vector((0.0, 0.0)).freeze(), radius: float = 1.0) -> ifcopenshell.entity_instance:
        """
        :param center: circle 2D position, defaults to zero-vector
        :type center: Vector, optional
        :param radius: radius of the circle, defaults to 1.0
        :type radius: float, optional

        :return: IfcCircle
        :rtype: ifcopenshell.entity_instance
        """
        ifc_center = self.file.createIfcAxis2Placement2D(self.file.createIfcCartesianPoint(center))
        ifc_curve = self.file.createIfcCircle(ifc_center, radius)

        #  self.file_file.createIfcAxis2Placement2D(tool.Ifc.get().createIfcCartesianPoint(center[0:2]))
        return ifc_curve

    def plane(
        self, location: Vector = Vector((0.0, 0.0, 0.0)).freeze(), normal: Vector = Vector((0.0, 0.0, 1.0)).freeze()
    ) -> ifcopenshell.entity_instance:
        """
        Create IfcPlane.

        :param location: plane position, defaults to `(0.0, 0.0, 0.0)`
        :type location: Vector, optional
        :param normal: plane normal direction, defaults to `(0.0, 0.0, 1.0)`
        :type normal: Vector, optional
        :return: IfcPlane
        :rtype: ifcopenshell.entity_instance
        """

        if normal.to_tuple(2) == Vector((0.0, 0.0, 1.0)):
            arbitrary_vector = Vector((0.0, 1.0, 0.0))
        else:
            arbitrary_vector = Vector((0.0, 0.0, 1.0))
        x_axis = normal.cross(arbitrary_vector).normalized()
        axis_placement = self.create_axis2_placement_3d(location, normal, x_axis)
        return self.file.createIfcPlane(axis_placement)

    # TODO: explain points order for the curve_between_two_points
    # because the order is important and defines the center of the curve
    # currently it seems like the first point shifted by x-axis defines the center
    def curve_between_two_points(self, points: tuple[Vector, Vector]) -> ifcopenshell.entity_instance:
        # > points - list of 2 Vectors
        """Simple circle based curve between two points
        Good for creating curves and fillets, won't work for continuous ellipse shapes.
        """
        diff = points[1] - points[0]
        max_diff_i = list(diff).index(max(diff, key=lambda x: abs(x)))
        diff_sign = V(*[(sign(e) if i == max_diff_i else 0) for i, e in enumerate(diff)])

        # diff should be applied only to one axis
        # if it's applied to two (like in a case of circle) it will create
        # a straight line instead of a curve
        diff = V(0.01, 0.01) * diff_sign
        middle_point = points[0] + diff
        points = [points[0], middle_point, points[1]]
        seg = self.file.createIfcArcIndex((1, 2, 3))
        ifc_points = self.file.createIfcCartesianPointList2D(points)
        curve = self.file.createIfcIndexedPolyCurve(Points=ifc_points, Segments=[seg])
        return curve

    def get_trim_points_from_mask(
        self,
        x_axis_radius: float,
        y_axis_radius: float,
        trim_points_mask: list[int],
        position_offset: Optional[Vector] = None,
    ) -> list[Vector]:
        """Handy way to get edge points of the ellipse like shape of a given radiuses.

        Mask points are numerated from 0 to 3 ccw starting from (x_axis_radius/2; 0).

        Example: mask (0, 1, 2, 3) will return points (x, 0), (0, y), (-x, 0), (0, -y)
        """
        points = (
            V(x_axis_radius, 0),
            V(0, y_axis_radius),
            V(-x_axis_radius, 0),
            V(0, -y_axis_radius),
        )
        if position_offset:
            trim_points = [points[i] + position_offset for i in trim_points_mask]
        else:
            trim_points = [points[i] for i in trim_points_mask]
        return trim_points

    def create_ellipse_curve(
        self,
        x_axis_radius: float,
        y_axis_radius: float,
        position=Vector((0.0, 0.0)).freeze(),
        trim_points: Sequence[Vector] = (),
        ref_x_direction: Vector = Vector((1.0, 0.0)),
        trim_points_mask: Sequence[int] = (),
    ) -> ifcopenshell.entity_instance:
        """
        Ellipse trimming points should be specified in counter clockwise order.

        For example, if you need to get the part of the ellipse ABOVE y-axis, you need to use mask (0,2). Below y-axis - (2,0)

        For more information about trim_points_mask check builder.get_trim_points_from_mask

        Notion: trimmed ellipse also contains polyline between trim points, meaning IfcTrimmedCurve could be used
        for further extrusion.
        """
        direction = self.file.createIfcDirection(ref_x_direction)
        ifc_position = self.file.createIfcAxis2Placement2D(
            self.file.createIfcCartesianPoint(position), RefDirection=direction
        )
        ifc_ellipse = self.file.createIfcEllipse(
            Position=ifc_position, SemiAxis1=x_axis_radius, SemiAxis2=y_axis_radius
        )

        if not trim_points:
            if not trim_points_mask:
                return ifc_ellipse
            trim_points = self.get_trim_points_from_mask(
                x_axis_radius, y_axis_radius, trim_points_mask, position_offset=position
            )

        trim1 = [self.file.createIfcCartesianPoint(trim_points[0])]
        trim2 = [self.file.createIfcCartesianPoint(trim_points[1])]

        trim_ellipse = self.file.createIfcTrimmedCurve(
            BasisCurve=ifc_ellipse, Trim1=trim1, Trim2=trim2, SenseAgreement=True, MasterRepresentation="CARTESIAN"
        )
        return trim_ellipse

    def profile(
        self,
        outer_curve: ifcopenshell.entity_instance,
        name: Optional[str] = None,
        inner_curves: Sequence[ifcopenshell.entity_instance] = (),
        profile_type: str = "AREA",
    ) -> ifcopenshell.entity_instance:
        # > inner_curves - list of IfcCurve;
        # inner_curves could be used as a tool for boolean operation
        # but if any point of inner curve will go outside the outer curve
        # it will just add shape on top instead of "boolean" it
        # because of that you can't create bool edges of outer_curve this way

        # < returns IfcArbitraryClosedProfileDef or IfcArbitraryProfileDefWithVoids

        if outer_curve.Dim != 2:
            raise Exception(
                f"Outer curve for IfcArbitraryClosedProfileDef/IfcIfcArbitraryProfileDefWithVoid should be 2D to be valid, currently it has {outer_curve.Dim} dimensions.\n"
                "Ref: https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcArbitraryClosedProfileDef.htm#8.15.3.1.4-Formal-propositions"
            )

        kwargs = {
            "ProfileName": name,
            "ProfileType": profile_type,
            "OuterCurve": outer_curve,
        }
        if self.file.schema == "IFC2X3":
            kwargs["Position"] = self.file.create_entity(
                "IfcAxis2Placement2D", self.file.create_entity("IfcCartesianPoint", [0.0, 0.0])
            )

        if inner_curves:
            if not isinstance(inner_curves, collections.abc.Iterable):
                inner_curves = [inner_curves]
                if any(curve.Dim != 2 for curve in inner_curves):
                    raise Exception(
                        "WARNING. InnerCurve for IfcIfcArbitraryProfileDefWithVoid sould be 2D to be valid, "
                        "currently on one of the inner curves is using different amount of dimensions.\n"
                        "Ref: https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcArbitraryClosedProfileDef.htm#8.15.3.1.4-Formal-propositions"
                    )

            profile = self.file.create_entity("IfcArbitraryProfileDefWithVoids", InnerCurves=inner_curves, **kwargs)
        else:
            profile = self.file.create_entity("IfcArbitraryClosedProfileDef", **kwargs)
        return profile

    def translate(
        self,
        curve_or_item: Union[ifcopenshell.entity_instance, list[ifcopenshell.entity_instance]],
        translation: Vector,
        create_copy: bool = False,
    ) -> Union[ifcopenshell.entity_instance, list[ifcopenshell.entity_instance]]:
        # > curve_or_item - could be a list of curves or items or representations
        # < returns translated object

        multiple_objects = isinstance(curve_or_item, collections.abc.Iterable)
        if not multiple_objects:
            curve_or_item = [curve_or_item]

        processed_objects = []
        for c in curve_or_item:
            if create_copy:
                c = ifcopenshell.util.element.copy_deep(self.file, c)

            if c.is_a() in ("IfcIndexedPolyCurve", "IfcPolyline"):
                coords = self.get_polyline_coords(c)
                coords = [Vector(co) + translation for co in coords]
                self.set_polyline_coords(c, coords)

            elif c.is_a("IfcCircle") or c.is_a("IfcExtrudedAreaSolid") or c.is_a("IfcEllipse"):
                base_position = Vector(c.Position.Location.Coordinates)
                c.Position.Location.Coordinates = base_position + translation

            elif c.is_a("IfcShapeRepresentation"):
                for item in c.Items:
                    self.translate(item, translation)

            elif c.is_a("IfcTrimmedCurve"):
                base_position = Vector(c.Trim1[0].Coordinates)
                c.Trim1[0].Coordinates = base_position + translation

                base_position = Vector(c.Trim2[0].Coordinates)
                c.Trim2[0].Coordinates = base_position + translation

                self.translate(c.BasisCurve, translation)

            else:
                raise Exception(f"{c} is not supported for translate() method.")

            processed_objects.append(c)

        return processed_objects if multiple_objects else processed_objects[0]

    def rotate_2d_point(
        self, point_2d: Vector, angle=90, pivot_point: Vector = Vector((0.0, 0.0)).freeze(), counter_clockwise=False
    ) -> Vector:
        # > angle - in degrees
        # < rotated Vector

        angle_rad = angle / 180 * pi * (1 if counter_clockwise else -1)
        relative_point = point_2d - pivot_point
        relative_point = Matrix.Rotation(angle_rad, 2, "Z") @ relative_point
        point_2d = relative_point + pivot_point
        return point_2d

    def rotate(
        self,
        curve_or_item: Union[ifcopenshell.entity_instance, list[ifcopenshell.entity_instance]],
        angle: float = 90,
        pivot_point: Vector = Vector((0.0, 0.0)).freeze(),
        counter_clockwise: bool = False,
        create_copy: bool = False,
    ) -> Union[ifcopenshell.entity_instance, list[ifcopenshell.entity_instance]]:
        # > curve_or_item - could be a list of curves or items
        # > angle - in degrees
        # < returns rotated object

        multiple_objects = isinstance(curve_or_item, collections.abc.Iterable)
        if not multiple_objects:
            curve_or_item = [curve_or_item]

        processed_objects = []
        for c in curve_or_item:
            if create_copy:
                c = ifcopenshell.util.element.copy_deep(self.file, c)

            if c.is_a() in ("IfcIndexedPolyCurve", "IfcPolyline"):
                original_coords = self.get_polyline_coords(c)
                coords = [
                    self.rotate_2d_point(Vector(co), angle, pivot_point, counter_clockwise) for co in original_coords
                ]
                self.set_polyline_coords(c, coords)

            elif c.is_a("IfcCircle"):
                base_position = Vector(c.Position.Location.Coordinates)
                new_position = self.rotate_2d_point(base_position, angle, pivot_point, counter_clockwise)
                c.Position.Location.Coordinates = new_position

            elif c.is_a("IfcExtrudedAreaSolid"):
                # TODO: add support for Z-axis too
                base_position = Vector(c.Position.Location.Coordinates)
                new_position = self.rotate_2d_point(base_position.to_2d(), angle, pivot_point, counter_clockwise)
                new_position = new_position.to_3d()
                new_position.z = base_position.z
                c.Position.Location.Coordinates = new_position

                # TODO: add inner axis too and test it
                self.rotate(c.SweptArea.OuterCurve, angle, pivot_point, counter_clockwise)

            else:
                raise Exception(f"{c} is not supported for rotate() method.")

            processed_objects.append(c)

        return processed_objects if multiple_objects else processed_objects[0]

    def mirror_2d_point(
        self,
        point_2d: Vector,
        mirror_axes: Vector = Vector((1.0, 1.0)).freeze(),
        mirror_point: Vector = Vector((0.0, 0.0)).freeze(),
    ) -> Vector:
        """mirror_axes - along which axes mirror will be applied"""
        base = point_2d  # prevent mutating the argument
        mirror_axes = Vector([-1 if i > 0 else 1 for i in mirror_axes])
        relative_point = base - mirror_point
        relative_point = relative_point * mirror_axes
        point_2d = relative_point + mirror_point
        return point_2d

    def get_axis2_placement_3d_matrix(self, axis2_placement_3d: ifcopenshell.entity_instance) -> Matrix:
        """
        Generate a Matrix from IfcAxis2Placement3D.

        :param axis2_placement_3d: IfcAxis2Placement3D
        :type axis2_placement_3d: ifcopenshell.entity_instance
        :return: generated matrix
        :rtype: Matrix
        """
        p = axis2_placement_3d

        M = Matrix.Identity(3)
        x_axis = Vector(p.RefDirection.DirectionRatios)
        z_axis = Vector(p.Axis.DirectionRatios)

        x_angle = -x_axis.angle(M[0])
        rotation_vector = x_axis.cross(M[0])
        M_X_rotation = Matrix.Rotation(x_angle, 3, rotation_vector)

        z_angle = -z_axis.angle(M[2])
        rotation_vector = z_axis.cross(M[2])
        M_Z_rotation = Matrix.Rotation(z_angle, 3, rotation_vector)
        rotation_matrix = M_X_rotation @ M_Z_rotation

        return rotation_matrix

    def create_axis2_placement_3d(
        self,
        position: VectorTuple = (0.0, 0.0, 0.0),
        z_axis: VectorTuple = (0.0, 0.0, 1.0),
        x_axis: VectorTuple = (1.0, 0.0, 0.0),
    ) -> ifcopenshell.entity_instance:
        """
        Create IfcAxis2Placement3D.

        :param position: placement position (Axis), defaults to `(0.0, 0.0, 0.0)`
        :type position: VectorTuple, optional
        :param z_axis: local Z axis direction, defaults to `(0.0, 0.0, 1.0)`
        :type z_axis: VectorTuple, optional
        :param x_axis: local X axis direction (RefDirection), defaults to `(1.0, 0.0, 0.0)`
        :type x_axis: VectorTuple, optional
        :return: IfcAxis2Placement3D
        :rtype: ifcopenshell.entity_instance
        """
        return self.file.createIfcAxis2Placement3D(
            self.file.createIfcCartesianPoint(position),
            Axis=self.file.createIfcDirection(z_axis),
            RefDirection=self.file.createIfcDirection(x_axis),
        )

    def create_axis2_placement_3d_from_matrix(
        self,
        matrix: Union[npt.NDArray[np.float64], None] = None,
    ) -> ifcopenshell.entity_instance:
        """
        Create IfcAxis2Placement3D from numpy matrix.

        :param matrix: 4x4 transformation matrix, defaults to `np.eye(4)`
        :type matrix: npt.NDArray[np.float64], optional
        :return: IfcAxis2Placement3D
        :rtype: ifcopenshell.entity_instance
        """
        if matrix is None:
            matrix = np.eye(4, dtype=float)
        return self.create_axis2_placement_3d(
            position=matrix[:, 3][:3].tolist(), z_axis=matrix[:, 2][:3].tolist(), x_axis=matrix[:, 0][:3].tolist()
        )

    def mirror(
        self,
        curve_or_item: Union[ifcopenshell.entity_instance, list[ifcopenshell.entity_instance]],
        mirror_axes: Vector = Vector((1.0, 1.0)).freeze(),
        mirror_point: Vector = Vector((0.0, 0.0)).freeze(),
        create_copy: bool = False,
        placement_matrix: Optional[Matrix] = None,
    ) -> Union[ifcopenshell.entity_instance, list[ifcopenshell.entity_instance]]:
        """mirror_axes - along which axes mirror will be applied

        For example, mirroring `A(1,0)` by axis `(1,0)` will result in `A'(-1,0)`
        """
        # > curve_or_item - could be a list of curves or items
        # > mirror_axes - could be a list of mirrors to apply to curve_or_item
        # multiple mirror_axes will result in multiple resulting curves
        # example: curve_or_item = [a, b], mirror_axes=[v1, v2], result = [av1, av2, bv1, bv2]
        # < returns mirrored object

        # TODO: need to add placement_matrix for other types besides polycurve?

        multiple_objects = isinstance(curve_or_item, collections.abc.Iterable)
        curve_or_item = [curve_or_item] if not multiple_objects else curve_or_item
        multiple_transformations = isinstance(mirror_axes, collections.abc.Iterable)
        mirror_axes_data = [mirror_axes] if not multiple_transformations else mirror_axes

        processed_objects = []
        for curve_or_item_el in curve_or_item:
            for mirror_axes in mirror_axes_data:
                c = (
                    ifcopenshell.util.element.copy_deep(self.file, curve_or_item_el)
                    if create_copy
                    else curve_or_item_el
                )

                if c.is_a() in ("IfcIndexedPolyCurve", "IfcPolyline"):
                    original_coords = self.get_polyline_coords(c)
                    inverted_placement_matrix = placement_matrix.inverted() if placement_matrix else None
                    coords = []
                    for co in original_coords:
                        co_base = Vector(co)
                        if placement_matrix:
                            # TODO: add support for Z-axis too
                            co_base = placement_matrix @ co_base.to_3d()
                            co = self.mirror_2d_point(co_base.to_2d(), mirror_axes, mirror_point).to_3d()
                            co.z = co_base.z
                            co = (inverted_placement_matrix @ co).to_2d()
                        else:
                            co = self.mirror_2d_point(co_base, mirror_axes, mirror_point)

                        coords.append(co)

                    self.set_polyline_coords(c, coords)

                elif c.is_a("IfcCircle") or c.is_a("IfcEllipse"):
                    base_position = Vector(c.Position.Location.Coordinates)
                    new_position = self.mirror_2d_point(base_position, mirror_axes, mirror_point)
                    c.Position.Location.Coordinates = new_position

                elif c.is_a("IfcExtrudedAreaSolid"):
                    placement_matrix = self.get_axis2_placement_3d_matrix(c.Position)
                    base_position = Vector(c.Position.Location.Coordinates)
                    # TODO: add support for Z-axis too
                    new_position = self.mirror_2d_point(base_position.to_2d(), mirror_axes, mirror_point)
                    new_position = new_position.to_3d()
                    new_position.z = base_position.z
                    c.Position.Location.Coordinates = new_position

                    # TODO: add support for Z-axis too
                    self.translate(c.SweptArea.OuterCurve, base_position.to_2d())
                    self.mirror(c.SweptArea.OuterCurve, mirror_axes, mirror_point, placement_matrix=placement_matrix)
                    self.translate(c.SweptArea.OuterCurve, -new_position.to_2d())

                    if hasattr(c.SweptArea, "InnerCurves"):
                        for inner_curve in c.SweptArea.InnerCurves:
                            self.translate(inner_curve, base_position.to_2d())
                            self.mirror(inner_curve, mirror_axes, mirror_point, placement_matrix=placement_matrix)
                            self.translate(inner_curve, -new_position.to_2d())

                    # extrusion converted to world space
                    base_extruded_direction = Vector(c.ExtrudedDirection.DirectionRatios)
                    extruded_direction = placement_matrix @ base_extruded_direction

                    # TODO: add support for Z-axis too
                    # mirror point is ignored for extrusion direction
                    new_direction = self.mirror_2d_point(extruded_direction.to_2d(), mirror_axes, mirror_point=V(0, 0))
                    new_direction = new_direction.to_3d()
                    new_direction.z = extruded_direction.z

                    # extrusion direction converted back to placement space
                    new_direction = placement_matrix.inverted() @ new_direction
                    c.ExtrudedDirection.DirectionRatios = new_direction

                elif c.is_a("IfcTrimmedCurve"):
                    trim_coords = [c.Trim1[0].Coordinates, c.Trim2[0].Coordinates]
                    trim_coords = [Vector(coords) for coords in trim_coords]
                    trim_coords = [
                        self.mirror_2d_point(base_position, mirror_axes, mirror_point) for base_position in trim_coords
                    ]

                    # if mirror only by 1 axis we need to preserve the counter-clockwise order
                    # for the trim points
                    if 0 in mirror_axes:
                        trim_coords = [trim_coords[1], trim_coords[0]]

                    base_position = Vector(c.Trim1[0].Coordinates)
                    c.Trim1[0].Coordinates, c.Trim2[0].Coordinates = trim_coords

                    self.mirror(c.BasisCurve, mirror_axes, mirror_point)
                else:
                    raise Exception(f"{c} is not supported for mirror() method.")

                processed_objects.append(c)

        return processed_objects if (multiple_objects or multiple_transformations) else processed_objects[0]

    def sphere(self, radius: float = 1.0, center: VectorTuple = (0.0, 0.0, 0.0)) -> ifcopenshell.entity_instance:
        """
        :param radius: radius of the sphere, defaults to 1.0
        :type radius: float, optional
        :param center: sphere position, defaults to `(0.0, 0.0, 0.0)`
        :type center: VectorTuple, optional

        :return: IfcSphere
        :rtype: ifcopenshell.entity_instance
        """

        ifc_position = self.create_axis2_placement_3d(position=center)
        return self.file.createIfcSphere(Radius=radius, Position=ifc_position)

    def extrude(
        self,
        profile_or_curve: ifcopenshell.entity_instance,
        magnitude: float = 1.0,
        position: Vector = Vector([0.0, 0.0, 0.0]).freeze(),
        extrusion_vector: Vector = Vector((0.0, 0.0, 1.0)).freeze(),
        position_z_axis: Vector = Vector((0.0, 0.0, 1.0)).freeze(),
        position_x_axis: Vector = Vector((1.0, 0.0, 0.0)).freeze(),
        position_y_axis: Optional[Vector] = None,
    ) -> ifcopenshell.entity_instance:
        """Extrude profile or curve to get IfcExtrudedAreaSolid.

        REMEMBER when handling custom axes - IFC is using RIGHT handed coordinate system.

        Position and position axes are in world space, extrusion vector in placement space defined by
        position_x_axis/position_y_axis/position_z_axis

        NOTE: changing position also changes the resulting geometry origin.

        """
        # > profile_or_curve
        # > extrusion vector - as defined in coordinate system position_x_axis+position_z_axis
        # > position - as defined in default IFC coordinate system, not in position_x_axis+position_z_axis
        # > position_y_axis - optional, could be used to calculate Z-axis based on Y-axis
        # < IfcExtrudedAreaSolid

        if not magnitude:
            raise Exception(
                "Extrusion magnitude must be greater than 0 to be valid.\n"
                "Ref: https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcPositiveLengthMeasure.htm#8.11.2.71.3-Formal-representation"
            )

        if not profile_or_curve.is_a("IfcProfileDef"):
            profile_or_curve = self.profile(profile_or_curve)

        if position_y_axis:
            position_z_axis = position_x_axis.cross(position_y_axis)

        ifc_position = self.create_axis2_placement_3d(position, position_z_axis, position_x_axis)
        ifc_direction = self.file.createIfcDirection(extrusion_vector)
        extruded_area = self.file.createIfcExtrudedAreaSolid(
            SweptArea=profile_or_curve, Position=ifc_position, ExtrudedDirection=ifc_direction, Depth=magnitude
        )
        return extruded_area

    def create_swept_disk_solid(
        self, path_curve: ifcopenshell.entity_instance, radius: float
    ) -> ifcopenshell.entity_instance:
        """Create IfcSweptDiskSolid from `path_curve` (must be 3D) and `radius`"""
        if path_curve.Dim != 3:
            raise Exception(
                f"Path curve for IfcSweptDiskSolid should be 3D to be valid, currently it has {path_curve.Dim} dimensions.\n"
                "Ref: https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcSweptDiskSolid.htm#8.8.3.42.4-Formal-propositions"
            )

        disk_solid = self.file.createIfcSweptDiskSolid(Directrix=path_curve, Radius=radius)
        return disk_solid

    def get_representation(
        self,
        context: ifcopenshell.entity_instance,
        items: Union[ifcopenshell.entity_instance, list[ifcopenshell.entity_instance]],
        representation_type: Optional[str] = None,
    ) -> ifcopenshell.entity_instance:
        """Create IFC representation for the specified context and items.

        :param context: IfcGeometricRepresentationSubContext
        :type context: ifcopenshell.entity_instance
        :param items: could be a list or single curve/IfcExtrudedAreaSolid
        :param representation_type: Explicitly specified RepresentationType, defaults to `None`.
            If not provided it will be guessed from the items types
        :type representation_type: str, optional

        :return: IfcShapeRepresentation
        :rtype: ifcopenshell.entity_instance
        """
        if not isinstance(items, collections.abc.Iterable):
            items = [items]

        item_types = set([i.is_a() for i in items])
        if not representation_type:
            if "IfcSweptDiskSolid" in item_types:
                representation_type = "AdvancedSweptSolid"
            elif "IfcExtrudedAreaSolid" in item_types:
                representation_type = "SweptSolid"
            elif "IfcCsgSolid" in item_types:
                representation_type = "CSG"
            elif items[0].is_a("IfcTessellatedItem"):
                representation_type = "Tessellation"
            elif items[0].is_a("IfcCurve") and items[0].Dim == 3:
                representation_type = "Curve3D"
            else:
                representation_type = "Curve2D"

        representation = self.file.createIfcShapeRepresentation(
            ContextOfItems=context,
            RepresentationIdentifier=context.ContextIdentifier,
            RepresentationType=representation_type,
            Items=items,
        )
        return representation

    def deep_copy(self, element: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
        return ifcopenshell.util.element.copy_deep(self.file, element)

    # UTILITIES
    def extrude_kwargs(self, axis: Literal["Y", "X", "Z"]) -> dict[str, Vector]:
        """Shortcut to get kwargs for `ShapeBuilder.extrude` to extrude by some axis.

        It assumes you have 2D profile in:
            XZ plane for Y axis extrusion, \n
            YZ plane for X axis extrusion, \n
            XY plane for Z axis extrusion, \n

        Extruding by X/Y using other kwargs might break ValidExtrusionDirection."""

        axis = axis.upper()

        if axis == "Y":
            return {
                "position_x_axis": Vector((1, 0, 0)),
                "position_z_axis": Vector((0, -1, 0)),
                "extrusion_vector": Vector((0, 0, -1)),
            }
        elif axis == "X":
            return {
                "position_x_axis": Vector((0, 1, 0)),
                "position_z_axis": Vector((1, 0, 0)),
                "extrusion_vector": Vector((0, 0, 1)),
            }
        elif axis == "Z":
            return {
                "position_x_axis": Vector((1, 0, 0)),
                "position_z_axis": Vector((0, 0, 1)),
                "extrusion_vector": Vector((0, 0, 1)),
            }

    def rotate_extrusion_kwargs_by_z(
        self, kwargs: dict[str, Any], angle: float, counter_clockwise: bool = False
    ) -> dict[str, Vector]:
        """shortcut to rotate extrusion kwargs by z axis

        `kwargs` expected to have `position_x_axis` and `position_z_axis` keys

        `angle` is a rotation value in radians

        by default rotation is clockwise, to make it counter clockwise use `counter_clockwise` flag
        """
        rot = Matrix.Rotation(-angle, 3, "Z")
        kwargs = kwargs.copy()  # prevent mutation of original kwargs
        kwargs["position_x_axis"].rotate(rot)
        kwargs["position_z_axis"].rotate(rot)
        return kwargs

    def get_polyline_coords(self, polyline: ifcopenshell.entity_instance) -> list[Vector]:
        """polyline should be either `IfcIndexedPolyCurve` or `IfcPolyline`"""
        coords = None
        if polyline.is_a("IfcIndexedPolyCurve"):
            coords = polyline.Points.CoordList
        elif polyline.is_a("IfcPolyline"):
            coords = [p.Coordinates for p in polyline.Points]
        return coords

    def set_polyline_coords(self, polyline: ifcopenshell.entity_instance, coords: list[Vector]) -> None:
        """polyline should be either `IfcIndexedPolyCurve` or `IfcPolyline`"""
        if polyline.is_a("IfcIndexedPolyCurve"):
            polyline.Points.CoordList = coords
        elif polyline.is_a("IfcPolyline"):
            for i, co in enumerate(coords):
                polyline.Points[i].Coordinates = co

    def get_simple_2dcurve_data(
        self,
        coords: list[Vector],
        fillets: Sequence[int] = (),
        fillet_radius: Sequence[float] = (),
        closed: bool = True,
        create_ifc_curve: bool = False,
    ) -> tuple[list[Vector], list[tuple[int, int], Union[ifcopenshell.entity_instance, None]]]:
        """
        Creates simple 2D curve from set of 2d coords and list of points with fillets.
        Simple curve means that all fillets are based on 90 degree angle.

        > coords:        list of 2d coords. Example: ((x0,y0), (x1,y1), (x2, y2))
        > fillets:       list of points from `coords` to base fillet on. Example: (1,)
        > fillet_radius: list of fillet radius for each of corresponding point form `fillets`. Example: (5.,)
        Note: filler_radius could be just 1 float value if it's the same for all fillets.

        Optional arguments:
        > closed:           boolean whether curve should be closed (whether last point connected to first one). Default: True
        > create_ifc_curve: create IfcIndexedPolyCurve or just return the data. Default: False

        < returns (points, segments, ifc_curve) for the created simple curve
        if both points in e are equally far from pt, then v1 is returned."""

        def remove_redundant_points(points, segments):
            # prevent mutating
            points = [tuple(p) for p in points]
            segments = segments.copy()

            # find duplicate points, reindex them in segments
            # and mark them to delete later
            points_to_remove = []
            prev_point = 0
            for i, p in enumerate(points[1:], 1):
                if p != points[prev_point]:
                    prev_point = i
                    continue

                valid_segments = []
                for s in segments:
                    s = [ps if ps != i else prev_point for ps in s]
                    valid_segments.append(s)
                segments = valid_segments
                points_to_remove.append(i)

            # remove duplicate segments
            valid_segments = [segment for segment in segments if len(set(segment)) != 1]
            points = [point for i, point in enumerate(points) if i not in points_to_remove]
            # correct the order in segments
            unique_points = sorted(set(chain(*valid_segments)))
            unique_points_translation = {prev: i for i, prev in enumerate(unique_points)}
            valid_segments = [[unique_points_translation[p] for p in s] for s in valid_segments]

            return points, valid_segments

        # option to use same fillet radius for all fillets
        if isinstance(fillet_radius, float):
            fillet_radius = [fillet_radius] * len(fillets)

        fillets = dict(zip(fillets, fillet_radius))
        segments = []
        points = []
        for co_i, co in enumerate(coords, 0):
            current_point = len(points)
            if co_i in fillets:
                r = fillets[co_i]
                rsb = r * cos(pi / 4)  # radius shift big
                rss = r - rsb  # radius shift small

                next_co = coords[(co_i + 1) % len(coords)]
                previous_co = coords[co_i - 1]

                # identify fillet type (1 of 4 possible types)
                x_direction = 1 if coords[co_i][0] < previous_co[0] or coords[co_i][0] < next_co[0] else -1
                y_direction = 1 if coords[co_i][1] < previous_co[1] or coords[co_i][1] < next_co[1] else -1

                xshift_point = (co[0] + r * x_direction, co[1])
                middle_point = (co[0] + rss * x_direction, co[1] + rss * y_direction)
                yshift_point = (co[0], co[1] + r * y_direction)

                # identify fillet direction
                if co[1] == previous_co[1]:
                    points.extend((xshift_point, middle_point, yshift_point))
                else:
                    points.extend((yshift_point, middle_point, xshift_point))

                segments.append([current_point - 1, current_point])
                segments.append([current_point, current_point + 1, current_point + 2])
            else:
                points.append(co)
                if co_i != 0:
                    segments.append([current_point - 1, current_point])

        if closed:
            segments.append([len(points) - 1, 0])

        # replace negative index
        if segments[0][0] == -1:
            segments[0][0] = len(points) - 1

        # sometime fillet points could match previous or next points in line
        # I remove them at the end to avoid making fillet algorithm even less readable
        points, segments = remove_redundant_points(points, segments)
        ifc_curve = None
        if create_ifc_curve:
            ifc_points = self.file.createIfcCartesianPointList2D(points)
            ifc_segments = []
            for segment in segments:
                segment = [i + 1 for i in segment]
                if len(segment) == 2:
                    ifc_segments.append(self.file.createIfcLineIndex(segment))
                elif len(segment) == 3:
                    ifc_segments.append(self.file.createIfcArcIndex(segment))

            ifc_curve = self.file.createIfcIndexedPolyCurve(Points=ifc_points, Segments=ifc_segments)
        return (points, segments, ifc_curve)

    def create_z_profile_lips_curve(
        self,
        FirstFlangeWidth: float,
        SecondFlangeWidth: float,
        Depth: float,
        Girth: float,
        WallThickness: float,
        FilletRadius: float,
    ) -> ifcopenshell.entity_instance:
        x1 = FirstFlangeWidth
        x2 = SecondFlangeWidth
        y = Depth / 2
        g = Girth
        t = WallThickness
        r = FilletRadius

        # fmt: off
        coords = (
            (-t/2,   y),
            (x2,     y),
            (x2,     y-g),
            (x2-t,   y-g),
            (x2-t,   y-t),
            (t/2,    y-t),
            (t/2,   -y),
            (-x1,   -y),
            (-x1,   -y+g),
            (-x1+t, -y+g),
            (-x1+t, -y+t),
            (-t/2,  -y+t)
        )

        # option for no additional thickness in outer radius:
        # points, segments, ifc_curve = create_curve_from_coords(
        #   coords, fillets = (0, 1, 4, 5, 6, 7, 10, 11), fillet_radius=r, closed=True, ifc_file=ifc_file
        # )

        points, segments, ifc_curve = self.get_simple_2dcurve_data(
            coords,
            fillets =     (0,   1,   4, 5, 6,   7,   10, 11),
            fillet_radius=(r+t, r+t, r, r, r+t, r+t, r, r),
            closed=True, create_ifc_curve=True)
        # fmt: on

        return ifc_curve

    def create_transition_arc_ifc(
        self, width: str, height: str, create_ifc_curve: bool = False
    ) -> tuple[list[Vector], list[tuple[int, int], Union[ifcopenshell.entity_instance, None]]]:
        # create an arc in the rectangle with specified width and height
        # if it's not possible to make a complete arc
        # it will create arc with longest radius possible
        # and straight segment in the middle
        fillet_size = (width / 2) / height
        if fillet_size <= 1:
            fillet_radius = height * fillet_size
            curve_coords = [
                (0.0, 0.0),
                (0.0, height),
                (width * 0.5, height),
                (width, height),
                (width, 0.0),
            ]
            fillets = (1, 3)
        else:
            fillet_radius = height
            curve_coords = [
                (0.0, 0.0),
                (0.0, height),
                (fillet_radius, height),
                (width - fillet_radius, height),
                (width, height),
                (width, 0.0),
            ]
            fillets = (1, 4)
        points, segments, transition_arc = self.get_simple_2dcurve_data(
            curve_coords, fillets, fillet_radius, closed=False, create_ifc_curve=create_ifc_curve
        )
        return points, segments, transition_arc

    def polygonal_face_set(self, points: list[Vector], faces: list[list[int]]) -> ifcopenshell.entity_instance:
        """
        Generate an IfcPolygonalFaceSet.

        :param points: rectangle size, could be either 2d or 3d, defaults to `(1,1)`
        :param faces: list of faces consisted of point indices (points indices starting from 0)
        :return: IfcPolygonalFaceSet
        """

        ifc_points = self.file.createIfcCartesianPointList3D(points)
        ifc_faces = []
        for face in faces:
            face = [i + 1 for i in face]
            ifc_faces.append(self.file.createIfcIndexedPolygonalFace(face))

        face_set = self.file.createIfcPolygonalFaceSet(Coordinates=ifc_points, Faces=ifc_faces)

        return face_set

    def extrude_face_set(
        self,
        points: list[Vector],
        magnitude: float,
        extrusion_vector: Vector = V(0, 0, 1).freeze(),
        offset: Optional[Vector] = None,
        start_cap: bool = True,
        end_cap: bool = True,
    ) -> ifcopenshell.entity_instance:
        """
        Method to extrude by creating face sets rather than creating IfcExtrudedAreaSolid.

        Useful if your representation is already using face sets and you need to avoid using SweptSolid
        to assure CorrectItemsForType.

        :param points: list of points, assuming they form consecutive closed polyline.
        :type points: list[Vector]
        :param magnitude: extrusion magnitude
        :type magnitude: float
        :param extrusion_vector: extrusion direction, by default it's extruding by Z+ axis
        :type extrusion_vector: Vector, optional
        :param offset: offset from the points
        :type offset: Vector, optional
        :param start_cap: if True, create start cap, by default it's True
        :type start_cap: bool, optional
        :param end_cap: if True, create end cap, by default it's True
        :type end_cap: bool, optional

        :return: IfcPolygonalFaceSet
        :rtype: ifcopenshell.entity_instance
        """

        # prevent mutating arguments, deepcopy doesn't work
        start_points = [p.copy() if not offset else (p + offset) for p in points]
        extrusion_offset = magnitude * extrusion_vector
        end_points = [p + extrusion_offset for p in start_points]

        points = start_points + end_points
        faces = []
        n_verts = len(start_points)
        last_vert_i = n_verts - 1
        for i in range(last_vert_i):
            face = (i, i + 1, n_verts + i + 1, n_verts + i)
            faces.append(face)
        faces.append((last_vert_i, 0, n_verts + 0, n_verts + last_vert_i))  # close the loop

        if end_cap:
            faces.append(tuple(range(n_verts, n_verts * 2)))
        if start_cap:
            faces.append(tuple(reversed(range(n_verts))))

        face_set = self.polygonal_face_set(points, faces)
        return face_set

    # TODO: move MEP to separate shape builder sub module
    def mep_transition_shape(
        self, start_segment, end_segment, start_length, end_length, angle=30.0, profile_offset=V(0, 0).freeze()
    ):
        """
        returns tuple of Model/Body/MODEL_VIEW IfcRepresentation and transition shape data
        """
        # good default values from angle = 30/60 deg
        # 30 degree angle will result in 75 degrees on the transition (= 90 - α/2) - https://i.imgur.com/tcoYDWu.png

        # TODO: get rid of reliance on profiles
        def get_profile(element):
            material = ifcopenshell.util.element.get_material(element, should_skip_usage=True)
            if material and material.is_a("IfcMaterialProfileSet") and len(material.MaterialProfiles) == 1:
                return material.MaterialProfiles[0].Profile

        def get_circle_points(radius, segments=16):
            """starting from (R,0), going counter-clockwise"""
            angle_d = 2 * pi / segments
            verts = []
            for i in range(segments):
                angle = angle_d * i
                verts.append(V(cos(angle), sin(angle), 0) * radius)
            return verts

        def get_rectangle_points(dim):
            """Starting from (+X/2, +Y/2) going counter-clockwise"""
            dim = dim / 2
            points = [
                dim * V(1, 1, 0),
                dim * V(-1, 1, 0),
                dim * V(-1, -1, 0),
                dim * V(1, -1, 0),
            ]
            return points

        # TODO: support more profiles
        def get_dim(profile, depth):
            if profile.is_a("IfcRectangleProfileDef"):
                return V(profile.XDim / 2, profile.YDim / 2, depth)
            elif profile.is_a("IfcCircleProfileDef"):
                return V(profile.Radius, profile.Radius, depth)
            return None

        start_profile = get_profile(start_segment)
        end_profile = get_profile(end_segment)

        start_half_dim = get_dim(start_profile, start_length)
        end_half_dim = get_dim(end_profile, end_length)

        # if profile types are not supported
        if not start_half_dim or not end_half_dim:
            return None, None

        transition_items = []
        start_offset = V(0, 0, start_length)
        end_extrusion_offset = start_offset.copy()

        transition_length = self.mep_transition_length(start_half_dim, end_half_dim, angle, profile_offset)
        if transition_length is None:
            return None, None

        faces = []
        end_extrusion_offset.z += transition_length
        end_extrusion_offset.xy += profile_offset

        if start_profile.is_a("IfcRectangleProfileDef") and end_profile.is_a("IfcRectangleProfileDef"):
            # no transitions for exactly the same profiles
            if transition_length == 0:
                return None, None

            faces += [(3, 4, 7, 0), (11, 8, 15, 12), (3, 11, 12, 4), (7, 15, 8, 0)]

            # NOTE: clockwise order for correct face orientation
            faces += [
                # start extrusion
                (0, 1, 2, 3),
                (8, 11, 10, 9),
                (0, 8, 9, 1),
                (1, 9, 10, 2),
                (2, 10, 11, 3),
                # end extrusion
                (4, 5, 6, 7),
                (12, 15, 14, 13),
                (4, 12, 13, 5),
                (5, 13, 14, 6),
                (6, 14, 15, 7),
            ]
            points = [
                start_half_dim * V(-1, -1, 1),
                start_half_dim * V(-1, -1, 0),
                start_half_dim * V(1, -1, 0),
                start_half_dim * V(1, -1, 1),
                end_half_dim * V(1, -1, 0) + end_extrusion_offset,
                end_half_dim * V(1, -1, 1) + end_extrusion_offset,
                end_half_dim * V(-1, -1, 1) + end_extrusion_offset,
                end_half_dim * V(-1, -1, 0) + end_extrusion_offset,
                start_half_dim * V(-1, 1, 1),
                start_half_dim * V(-1, 1, 0),
                start_half_dim * V(1, 1, 0),
                start_half_dim * V(1, 1, 1),
                end_half_dim * V(1, 1, 0) + end_extrusion_offset,
                end_half_dim * V(1, 1, 1) + end_extrusion_offset,
                end_half_dim * V(-1, 1, 1) + end_extrusion_offset,
                end_half_dim * V(-1, 1, 0) + end_extrusion_offset,
            ]
        elif start_profile.is_a("IfcCircleProfileDef") and end_profile.is_a("IfcCircleProfileDef"):
            # no transitions for exactly the same profiles
            if transition_length == 0:
                return None, None

            n_segments = 16
            first_profile_points = get_circle_points(start_profile.Radius, n_segments)
            second_profile_points = get_circle_points(end_profile.Radius, n_segments)

            faces = []
            for i in range(n_segments):
                # For wrapping around the circle
                next_i = (i + 1) % n_segments
                face = [i, next_i, next_i + n_segments, i + n_segments]
                faces.append(face)

            transition_items.append(self.extrude_face_set(first_profile_points, start_length, end_cap=False))
            transition_items.append(
                self.extrude_face_set(second_profile_points, end_length, offset=end_extrusion_offset, start_cap=False)
            )

            first_profile_points = [p + start_offset for p in first_profile_points]
            second_profile_points = [p + end_extrusion_offset for p in second_profile_points]

            points = first_profile_points + second_profile_points

        else:  # one is circular, another one is rectangular
            # support transition from rectangle to circle of the same dimensions
            if transition_length == 0:
                transition_length = (start_length + end_length) / 2
                end_extrusion_offset.z += transition_length

            starting_with_circle = start_profile.is_a("IfcCircleProfileDef")
            if starting_with_circle:
                circle_profile, rect_profile = start_profile, end_profile
            else:
                circle_profile, rect_profile = end_profile, start_profile

            circle_points = get_circle_points(circle_profile.Radius)
            rect_points = get_rectangle_points(V(rect_profile.XDim, rect_profile.YDim, 0))

            if starting_with_circle:
                start_points, end_points = circle_points, rect_points
            else:
                start_points, end_points = rect_points, circle_points

            transition_items.append(self.extrude_face_set(start_points, start_length, end_cap=False))
            transition_items.append(
                self.extrude_face_set(end_points, end_length, offset=end_extrusion_offset, start_cap=False)
            )

            # offset verts
            if starting_with_circle:
                circle_points = [p + start_offset for p in circle_points]
                rect_points = [p + end_extrusion_offset for p in rect_points]
            else:
                rect_points = [p + start_offset for p in rect_points]
                circle_points = [p + end_extrusion_offset for p in circle_points]

            # circle verts are 0-15, rect verts are 16-19
            points = circle_points + rect_points
            transition_faces = [
                (0, 19, 16),  # base
                (0, 16, 1),
                (1, 16, 2),
                (2, 16, 3),
                (3, 16, 4),
                (4, 16, 17),  # base
                (4, 17, 5),
                (5, 17, 6),
                (6, 17, 7),
                (7, 17, 8),
                (8, 17, 18),  # base
                (8, 18, 9),
                (9, 18, 10),
                (10, 18, 11),
                (11, 18, 12),
                (12, 18, 19),  # base
                (12, 19, 13),
                (13, 19, 14),
                (14, 19, 15),
                (15, 19, 0),
            ]
            # revert them in case it's starting with circle profile to keep the face orientation
            if starting_with_circle:
                transition_faces = [f[::-1] for f in transition_faces]
            faces += transition_faces

        face_set = self.polygonal_face_set(points, faces)
        transition_items.append(face_set)

        body = ifcopenshell.util.representation.get_context(self.file, "Model", "Body", "MODEL_VIEW")
        representation = self.get_representation(body, transition_items, "Tesselation")

        transition_data = {
            "start_length": start_length,
            "end_length": end_length,
            "angle": angle,
            "profile_offset": profile_offset,
            "transition_length": transition_length,
            "full_transition_length": start_length + transition_length + end_length,
        }

        return representation, transition_data

    # TODO: move to separate shape_builder method
    # so we could check transition length without creating representation
    def mep_transition_length(self, start_half_dim, end_half_dim, angle, profile_offset=V(0, 0).freeze(), verbose=True):
        """get the final transition length for two profiles dimensions, angle and XY offset between them,

        the difference from `calculate_transition` - `get_transition_length` is making sure
        that length will fit both sides of the transition
        """
        print = lambda *args, **kwargs: __builtins__["print"](*args, **kwargs) if verbose else None

        # vectors tend to have bunch of float point garbage
        # that can result in errors when we're calculating value for square root below
        offset = round_vector_to_precision(profile_offset, 1)
        diff = start_half_dim.xy - end_half_dim.xy
        diff = Vector([abs(i) for i in diff])

        print(f"offset = {profile_offset} / {offset}")
        print(f"diff = {diff}")

        calculation_arguments = {
            "start_half_dim": start_half_dim,
            "end_half_dim": end_half_dim,
            "diff": diff,
            "offset": offset,
            "verbose": verbose,
        }

        def check_transition(end_profile=False):
            length = self.mep_transition_calculate(**calculation_arguments, angle=angle, end_profile=end_profile)
            if length is None:
                return

            other_side_angle = self.mep_transition_calculate(
                **calculation_arguments, length=length, end_profile=not end_profile
            )

            # NOTE: for now we just hardcode the good value for that case
            same_dimension = is_x(diff.y if not end_profile else diff.x, 0)
            if same_dimension and is_x(offset.y if not end_profile else offset.x, 0):
                requested_angle = 90
            else:
                requested_angle = angle

            print(f"other_side_angle = {other_side_angle}, requested_angle = {requested_angle}")
            # need to make sure that the worst angle (maximum angle)
            # for this transition angle is `requested_angle`
            if other_side_angle < requested_angle or is_x(other_side_angle, requested_angle):
                print(f"final length = {length}, angle = {requested_angle}, other side angle = {other_side_angle}")
                return length

        return check_transition() or check_transition(True)

    def mep_transition_calculate(
        self, start_half_dim, end_half_dim, offset, diff=None, end_profile=False, angle=None, length=None, verbose=True
    ):
        """will return transition length based on the profile dimension differences and offset.

        If `length` is provided will return transition angle"""

        print = lambda *args, **kwargs: __builtins__["print"](*args, **kwargs) if verbose else None

        if diff is None:
            diff = start_half_dim.xy - end_half_dim.xy
            diff = Vector([abs(i) for i in diff])

        if end_profile:
            diff, offset = diff.yx, offset.yx

        same_dimension = is_x(diff.x, 0)
        a = diff.x + offset.x
        b = diff.x - offset.x
        if length is None:
            if not same_dimension:
                t = tan(radians(angle))
                h0 = a**2 + 4 * a * b * t**2 + 2 * a * b + b**2
                # TODO: we might need to specify the exact failing cases in the future
                if h0 < 0:
                    print(
                        f"B. Coulndn't calculate transition length for angle = {angle}, offset = {offset}, diff = {diff}"
                    )
                    return None

                h = (a + b + sqrt(h0)) / (2 * t)
                length_squared = h**2 - offset.y**2
                if length_squared <= 0:
                    print(f"B. angle = {angle} requires h = {h} which is not possible with y offset = {offset.y}")
                    return None
                length = sqrt(length_squared)

                if verbose:
                    A = (end_half_dim if end_profile else start_half_dim) * V(1, 0, 0)
                    end_profile_offset = offset.to_3d() + V(0, 0, length)
                    D = (start_half_dim if end_profile else end_half_dim) * V(1, 0, 0)
                    B, C = -A, -D
                    C += end_profile_offset
                    D += end_profile_offset
                    tested_angle = degrees((A - D).angle(B - C))
                    print(f"A. length = {length}, requested angle = {angle}, tested angle = {tested_angle}")
            else:
                if is_x(offset.x, 0):
                    angle = 90  # NOTE: for now we just hardcode the good value for that case
                    h = start_half_dim.x / tan(radians(angle / 2))
                    length_squared = h**2 - offset.y**2
                    if length_squared <= 0:
                        print(f"B. angle = {angle} requires h = {h} which is not possible with y offset = {offset.y}")
                        return None
                    length = sqrt(length_squared)

                    if verbose:
                        O = V(0, 0, 0)
                        A = V(-start_half_dim.x, 0, length) + offset.to_3d()
                        B = A * V(-1, 1, 1)
                        tested_angle = degrees((A - O).angle(B - O))
                        print(f"B. length = {length}, requested angle = {angle}, tested angle = {tested_angle}")
                else:
                    h = offset.x / tan(radians(angle))
                    length_squared = h**2 - offset.y**2
                    if length_squared <= 0:
                        print(f"C. angle = {angle} requires h = {h} which is not possible with y offset = {offset.y}")
                        return None
                    length = sqrt(length_squared)

                    if verbose:
                        A = V(-start_half_dim.x, 0, 0)
                        H = A + V(0, 0, length)
                        H.y += offset.y
                        D = H.copy()
                        D.x += offset.x
                        tested_angle = degrees((H - A).angle(D - A))
                        print(f"C. length = {length}, requested angle = {angle}, tested angle = {tested_angle}")

            return length

        elif angle is None:
            if not same_dimension:
                if length == 0:
                    return 0

                h = sqrt(length**2 + offset.y**2)
                t = -h * (a + b) / (a * b - h**2)
                angle = degrees(atan(t))

            else:
                h = sqrt(length**2 + offset.y**2)
                if is_x(offset.x, 0):
                    angle = degrees(2 * atan(start_half_dim.x / h))
                else:
                    angle = degrees(atan(offset.x / h))
            return angle

    def mep_bend_shape(
        self,
        segment,
        start_length: float,
        end_length: float,
        angle: float,
        radius: float,
        bend_vector: Vector,
        flip_z_axis: bool,
    ) -> ifcopenshell.entity_instance:
        """

        :param segment: IfcFlowSegment for a bend.
            Note that for a bend start and end segments types should match.
        :type segment: ifcopenshell.entity_instance
        :param angle: bend angle, in radians
        :type angle: float
        :param radius: bend radius
        :type radius: float
        :param bend_vector: offset between start and end segments in local space of start segment
            used mainly to determine the second bend axis and it's direction (positive or negative),
            the actual magnitude of the vector is not important (though near zero values will be ignored).
        :type bend_vector: Vector
        :param flip_z_axis: since we cannot determine z axis direction from the profile offset,
            there is an option to flip it if bend is going by start segment Z- axis.
        :type flip_z_axis: bool

        :return: tuple of Model/Body/MODEL_VIEW IfcRepresentation and transition shape data
        """

        def get_profile(element):
            material = ifcopenshell.util.element.get_material(element, should_skip_usage=True)
            if material and material.is_a("IfcMaterialProfileSet") and len(material.MaterialProfiles) == 1:
                return material.MaterialProfiles[0].Profile

        def get_dim(profile, depth):
            if profile.is_a("IfcRectangleProfileDef"):
                return V(profile.XDim / 2, profile.YDim / 2, depth)
            elif profile.is_a("IfcCircleProfileDef"):
                return V(profile.Radius, profile.Radius, depth)
            return None

        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(self.file)
        profile = get_profile(segment)
        is_circular_profile = profile.is_a("IfcCircleProfileDef")
        profile_dim = get_dim(profile, start_length)

        rounded_bend_vector = round_vector_to_precision(bend_vector, si_conversion)
        lateral_axis = next(i for i in range(2) if not is_x(rounded_bend_vector[i], 0))
        non_lateral_axis = 1 if lateral_axis == 0 else 0
        lateral_sign = sign(bend_vector[lateral_axis])
        z_sign = -1 if flip_z_axis else 1

        rep_items = []

        # bend circle center
        O = V(0, 0, 0)
        O[lateral_axis] = (radius + profile_dim[lateral_axis]) * lateral_sign
        theta = angle

        def get_circle_point(angle, radius):
            point = V(0, 0, 0)
            angle -= pi / 2
            # fmt: off
            point.z             = z_sign       * cos(angle) * radius
            point[lateral_axis] = lateral_sign * sin(angle) * radius
            # fmt: on
            return point

        def get_circle_tangent(angle):
            tangent = V(0, 0, 0)
            tangent.z = cos(angle) * z_sign
            tangent[lateral_axis] = sin(angle) * lateral_sign
            return tangent

        def get_bend_representation_item():
            r = radius
            theta_segments = [0, theta / 2, theta]
            if is_circular_profile:
                r += profile_dim[lateral_axis]
                points = [get_circle_point(cur_theta, r) for cur_theta in theta_segments]
                arc_points = (1,)
            else:
                outer_r = r + 2 * profile_dim[lateral_axis]
                outer_points = [get_circle_point(cur_theta, outer_r) for cur_theta in theta_segments[::-1]]
                if is_x(r, 0):
                    points = [get_circle_point(theta, r)] + outer_points
                    arc_points = (2,)
                else:
                    inner_points = [get_circle_point(cur_theta, r) for cur_theta in theta_segments]
                    points = inner_points + outer_points
                    arc_points = (1, 4)

            points = [p + O for p in points]
            offset = V(0, 0, 0)
            offset.z = z_sign * start_length

            if is_circular_profile:
                bend_path = self.polyline(points, closed=False, arc_points=arc_points, position_offset=offset)
                bend = self.create_swept_disk_solid(bend_path, profile_dim[lateral_axis])
            else:
                main_axes = lambda v: getattr(v, "xy"[lateral_axis] + "z")
                offset[non_lateral_axis] = -profile_dim[non_lateral_axis]

                extrusion_kwargs = self.extrude_kwargs("XY"[non_lateral_axis])
                profile_curve = self.polyline([main_axes(p) for p in points], arc_points=arc_points, closed=True)
                bend = self.extrude(
                    self.profile(profile_curve), profile_dim[non_lateral_axis] * 2, position=offset, **extrusion_kwargs
                )
            return bend

        rep_items.append(get_bend_representation_item())
        if start_length:
            rep_items.append(self.extrude(profile, start_length, extrusion_vector=V(0, 0, z_sign)))
        if end_length:
            end_position = O + get_circle_point(theta, radius + profile_dim[lateral_axis])
            end_position.z += start_length * z_sign

            # define extrusion space for the segment after the bend
            z_axis = get_circle_tangent(theta)
            extrude_kwargs = {
                "position_z_axis": z_axis,
                "extrusion_vector": Vector((0, 0, 1)),
            }
            # since we are sure that tangent involves only two axis
            # it's safe to assume that non lateral axis is untouched
            if lateral_axis == 0:
                x_axis = z_axis.cross(Vector((0, 1, 0)))
            else:
                x_axis = Vector((1, 0, 0))
            extrude_kwargs["position_x_axis"] = x_axis

            rep_items.append(self.extrude(profile, end_length, end_position, **extrude_kwargs))

        body = ifcopenshell.util.representation.get_context(self.file, "Model", "Body", "MODEL_VIEW")
        rep = self.get_representation(body, rep_items)

        bend_data = {
            "start_length": start_length,
            "end_length": end_length,
            "radius": radius,
            "angle": degrees(theta),
            "lateral_axis": lateral_axis,
            "lateral_sign": lateral_sign,
            "z_axis_sign": -1 if flip_z_axis else 1,
            "main_profile_dimension": profile_dim[lateral_axis],
        }
        return rep, bend_data
