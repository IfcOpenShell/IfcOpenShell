# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2022 @Andrej730
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

import collections
import ifcopenshell
import ifcopenshell.api
from math import cos, sin, pi
from mathutils import Vector, Matrix

V = lambda *x: Vector([float(i) for i in x])
sign = lambda x: x and (1, -1)[x < 0]

# Note: using ShapeBuilder try not to reuse IFC elements in the process
# otherwise you might run into situation where builder.mirror or other operation
# is applied twice during one run to the same element
# which might produce undesirable results


class ShapeBuilder:
    def __init__(self, ifc_file):
        self.file = ifc_file

    def polyline(self, points, closed=False, position_offset=None):
        # > points - list of points formatted like ( (x0, y0), (x1, y1) )
        # < IfcIndexedPolyCurve
        segments = [(i, i + 1) for i in range(1, len(points))]
        if closed:
            segments.append((len(points), 1))
        if position_offset:
            points = [Vector(p) + position_offset for p in points]

        dimensions = len(points[0])
        if dimensions == 2:
            ifc_points = self.file.createIfcCartesianPointList2D(points)
        elif dimensions == 3:
            ifc_points = self.file.createIfcCartesianPointList3D(points)

        ifc_segments = [self.file.createIfcLineIndex(segment) for segment in segments]
        ifc_curve = self.file.createIfcIndexedPolyCurve(Points=ifc_points, Segments=ifc_segments)
        return ifc_curve

    def get_rectangle_coords(self, size: Vector = Vector((1.0, 1.0)).freeze(), position: Vector = None):

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

    def rectangle(self, size: Vector = Vector((1.0, 1.0)).freeze(), position: Vector = None):
        """
        function supports both 2d and 3d rectangle sizes

        if `position` not specified zero-vector will be used

        returns IfcIndexedPolyCurve
        """
        # < IfcIndexedPolyCurve
        return self.polyline(self.get_rectangle_coords(size, position), closed=True)

    def circle(self, center: Vector = Vector((0.0, 0.0)).freeze(), radius=1.0):
        # < returns IfcCircle
        ifc_center = self.file.createIfcAxis2Placement2D(self.file.createIfcCartesianPoint(center))
        ifc_curve = self.file.createIfcCircle(ifc_center, radius)

        #  self.file_file.createIfcAxis2Placement2D(tool.Ifc.get().createIfcCartesianPoint(center[0:2]))
        return ifc_curve

    # TODO: explain points order for the curve_between_two_points
    # because the order is important and defines the center of the curve
    # currently it seems like the first point shifted by x-axis defines the center
    def curve_between_two_points(self, points):
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

    def get_trim_points_from_mask(self, x_axis_radius, y_axis_radius, trim_points_mask, position_offset=None):
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
        x_axis_radius,
        y_axis_radius,
        position=Vector((0.0, 0.0)).freeze(),
        trim_points=[],
        ref_x_direction=Vector((1.0, 0.0)),
        trim_points_mask=[],
    ):
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

    def profile(self, outer_curve, name=None, inner_curves=[], profile_type="AREA"):
        # > inner_curves - list of IfcCurve;
        # inner_curves could be used as a tool for boolean operation
        # but if any point of inner curve will go outside the outer curve
        # it will just add shape on top instead of "boolean" it
        # because of that you can't create bool edges of outer_curve this way

        # < returns IfcArbitraryClosedProfileDef or IfcArbitraryProfileDefWithVoids
        if inner_curves:
            if not isinstance(inner_curves, collections.abc.Iterable):
                inner_curves = [inner_curves]

            profile = self.file.createIfcArbitraryProfileDefWithVoids(
                ProfileName=name, ProfileType=profile_type, OuterCurve=outer_curve, InnerCurves=inner_curves
            )
        else:
            profile = self.file.createIfcArbitraryClosedProfileDef(
                ProfileName=name, ProfileType=profile_type, OuterCurve=outer_curve
            )
        return profile

    def translate(self, curve_or_item, translation: Vector, create_copy=False):
        # > curve_or_item - could be a list of curves or items or representations
        # < returns translated object

        multiple_objects = isinstance(curve_or_item, collections.abc.Iterable)
        if not multiple_objects:
            curve_or_item = [curve_or_item]

        processed_objects = []
        for c in curve_or_item:
            if create_copy:
                c = ifcopenshell.util.element.copy_deep(self.file, c)

            if c.is_a("IfcIndexedPolyCurve"):
                coords = [Vector(co) + translation for co in c.Points.CoordList]
                c.Points.CoordList = coords

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
    ):

        # > angle - in degrees
        # < rotated Vector

        angle_rad = angle / 180 * pi * (1 if counter_clockwise else -1)
        relative_point = point_2d - pivot_point
        relative_point = Matrix.Rotation(angle_rad, 2, "Z") @ relative_point
        point_2d = relative_point + pivot_point
        return point_2d

    def rotate(
        self,
        curve_or_item,
        angle=90,
        pivot_point: Vector = Vector((0.0, 0.0)).freeze(),
        counter_clockwise=False,
        create_copy=False,
    ):
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

            if c.is_a("IfcIndexedPolyCurve"):
                coords = [
                    self.rotate_2d_point(Vector(co), angle, pivot_point, counter_clockwise) for co in c.Points.CoordList
                ]
                c.Points.CoordList = coords

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
    ):
        """mirror_axes - along which axes mirror will be applied"""
        base = point_2d  # prevent mutating the argument
        mirror_axes = Vector([-1 if i > 0 else 1 for i in mirror_axes])
        relative_point = base - mirror_point
        relative_point = relative_point * mirror_axes
        point_2d = relative_point + mirror_point
        return point_2d

    def get_axis2_placement_3d_matrix(self, axis2_placement_3d):
        # > IfcAxis2Placement3D
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

    def mirror(
        self,
        curve_or_item,
        mirror_axes: Vector = Vector((1.0, 1.0)).freeze(),
        mirror_point: Vector = Vector((0.0, 0.0)).freeze(),
        create_copy=False,
        placement_matrix=None,
    ):
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

                if c.is_a("IfcIndexedPolyCurve"):
                    inverted_placement_matrix = placement_matrix.inverted() if placement_matrix else None
                    coords = []
                    for co in c.Points.CoordList:
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

                    c.Points.CoordList = coords

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
                            self.translate(inner_curve, base_position)
                            self.mirror(inner_curve, mirror_axes, mirror_point, placement_matrix=placement_matrix)
                            self.translate(inner_curve, -new_position)

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

    def extrude(
        self,
        profile_or_curve,
        magnitude=1.0,
        position: Vector = Vector([0.0, 0.0, 0.0]).freeze(),
        extrusion_vector: Vector = Vector((0.0, 0.0, 1.0)).freeze(),
        position_z_axis: Vector = Vector((0.0, 0.0, 1.0)).freeze(),
        position_x_axis: Vector = Vector((1.0, 0.0, 0.0)).freeze(),
        position_y_axis: Vector = None,
    ):
        """Extrude profile or curve to get IfcExtrudedAreaSolid.

        REMEMBER when handling custom axes - IFC is using RIGHT handed coordinate system.

        Position and position axes are in world space, extrusion vector in placement space defined by
        position_x_axis/position_y_axis/position_z_axis
        """
        # > profile_or_curve
        # > extrusion vector - as defined in coordinate system position_x_axis+position_z_axis
        # > position - as defined in default IFC coordinate system, not in position_x_axis+position_z_axis
        # > position_y_axis - optional, could be used to calculate Z-axis based on Y-axis
        # < IfcExtrudedAreaSolid

        if profile_or_curve.is_a() not in ("IfcArbitraryClosedProfileDef", "IfcArbitraryProfileDefWithVoids"):
            profile_or_curve = self.profile(profile_or_curve)

        if position_y_axis:
            position_z_axis = position_x_axis.cross(position_y_axis)

        ifc_position = self.file.createIfcAxis2Placement3D(
            self.file.createIfcCartesianPoint(position),  # position
            self.file.createIfcDirection(position_z_axis),  # Z-axis / Axis
            self.file.createIfcDirection(position_x_axis),  # X-axis / RefDirection
        )
        ifc_direction = self.file.createIfcDirection(extrusion_vector)
        extruded_area = self.file.createIfcExtrudedAreaSolid(
            SweptArea=profile_or_curve, Position=ifc_position, ExtrudedDirection=ifc_direction, Depth=magnitude
        )
        return extruded_area

    def get_representation(self, context, items):
        # > items - could be a list or single curve/IfcExtrudedAreaSolid
        # < IfcShapeRepresentation
        if not isinstance(items, collections.abc.Iterable):
            items = [items]
        representation = self.file.createIfcShapeRepresentation(
            ContextOfItems=context,
            RepresentationIdentifier=context.ContextIdentifier,
            RepresentationType="SweptSolid" if items[0].is_a("IfcExtrudedAreaSolid") else "Curve2D",
            Items=items,
        )
        return representation

    def deep_copy(self, element):
        return ifcopenshell.util.element.copy_deep(self.file, element)
