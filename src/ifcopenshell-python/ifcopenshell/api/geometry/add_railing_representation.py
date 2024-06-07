# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2023 @Andrej730
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
from ifcopenshell.util.shape_builder import ShapeBuilder, V
from itertools import chain
from mathutils import Vector, Matrix
import collections
import mathutils
from math import pi, cos, sin, tan, radians
from typing import Literal, Optional, Any


def mm(x: float) -> float:
    """mm to meters shortcut for readability"""
    return x / 1000


def add_railing_representation(
    file: ifcopenshell.file,
    *,  # keywords only as this API implementation is probably not final
    # IfcGeometricRepresentationContext
    context: ifcopenshell.entity_instance,
    railing_type: Literal["WALL_MOUNTED_HANDRAIL"] = "WALL_MOUNTED_HANDRAIL",
    railing_path: list[Vector],
    use_manual_supports: bool = False,
    support_spacing: Optional[float] = None,
    railing_diameter: Optional[float] = None,
    clear_width: Optional[float] = None,
    terminal_type: Literal[
        "180",
        "TO_END_POST",
        "TO_WALL",
        "TO_FLOOR",
        "TO_END_POST_AND_FLOOR",
    ] = "180",
    height: Optional[float] = None,
    looped_path: bool = False,
    unit_scale: Optional[float] = None,
) -> ifcopenshell.entity_instance:
    """
    Units are expected to be in IFC project units.

    :param context: IfcGeometricRepresentationContext for the representation.
    :type context: ifcopenshell.entity_instance
    :param railing_type: Type of the railing. Defaults to "WALL_MOUNTED_HANDRAIL".
    :type railing_type: Literal["WALL_MOUNTED_HANDRAIL"], optional
    :param railing_path: A list of points coordinates for the railing path,
        coordinates are expected to be at the top of the railing, not at the center.
        If not provided, default path [(0, 0, 1), (1, 0, 1), (2, 0, 1)] (in meters) will be used
    :type railing_path: list[Vector], optional.
    :param use_manual_supports: If enabled, supports are added on every vertex on the edges of the railing path.
        If disabled, supports are added automatically based on the support spacing. Default to False.
    :type use_manual_supports: bool, optional
    :param support_spacing: Distance between supports if automatic supports are used. Defaults to 1m.
    :type support_spacing: float, optional
    :param railing_diameter: Railing diameter. Defaults to 50mm.
    :type railing_diameter: float, optional
    :param clear_width: Clear width between the railing and the wall. Defaults to 40mm.
    :type clear_width: float, optional
    :param terminal_type: type of the cap. Defaults to "180".
    :type terminal_type: Literal["180","TO_END_POST","TO_WALL","TO_FLOOR","TO_END_POST_AND_FLOOR"], optional
    :param height: defaults to 1m
    :type height: float, optional
    :param looped_path: Whether to end the railing on the first point of `railing_path`. Defaults to False.
    :type looped_path: bool, optional
    :param unit_scale: The unit scale as calculated by
        ifcopenshell.util.unit.calculate_unit_scale. If not provided, it
        will be automatically calculated for you.
    :type unit_scale: float, optional
    :return: IfcShapeRepresentation for a railing.
    :rtype: ifcopenshell.entity_instance

    """
    usecase = Usecase()
    usecase.file = file
    # define unit_scale first as it's going to be used setting default arguments
    settings: dict[str, Any] = {
        "unit_scale": ifcopenshell.util.unit.calculate_unit_scale(file) if unit_scale is None else unit_scale,
    }
    settings.update(
        {
            "context": context,
            "railing_type": railing_path,
            "railing_path": (
                railing_path
                if railing_path is not None
                else usecase.path_si_to_units([V(0, 0, 1), V(1, 0, 1), V(2, 0, 1)])
            ),
            "use_manual_supports": use_manual_supports,
            "support_spacing": support_spacing if support_spacing is not None else usecase.convert_si_to_unit(mm(1000)),
            "railing_diameter": (
                railing_diameter if railing_diameter is not None else usecase.convert_si_to_unit(mm(50))
            ),
            "clear_width": clear_width if clear_width is not None else usecase.convert_si_to_unit(mm(40)),
            "terminal_type": terminal_type,
            "height": height if height is not None else usecase.convert_si_to_unit(mm(1000)),
            "looped_path": looped_path,
        }
    )
    usecase.settings = settings

    if railing_type != "WALL_MOUNTED_HANDRAIL":
        raise Exception('Only "WALL_MOUNTED_HANDRAIL" railing_type is supported at the moment.')
    return usecase.execute()


class Usecase:
    def execute(self):
        arc_points = []
        items_3d = []
        builder = ShapeBuilder(self.file)
        z_down = V(0, 0, -1)

        # measurements
        # from settings
        use_manual_supports = self.settings["use_manual_supports"]
        railing_radius = self.settings["railing_diameter"] / 2
        support_spacing = self.settings["support_spacing"]
        clear_width = self.settings["clear_width"]
        # for calculations purposes we use height without railing radius
        height = self.settings["height"] - railing_radius
        cap_type = self.settings["terminal_type"]
        ifc_context = self.settings["context"]
        railing_coords = self.settings["railing_path"]
        looped_path = self.settings["looped_path"]
        railing_coords = [p - z_down * railing_radius for p in railing_coords]

        # constant
        terminal_radius = self.convert_si_to_unit(mm(150))
        railing_fillet_radius = self.convert_si_to_unit(mm(100))
        support_length = clear_width + railing_radius
        support_radius = self.convert_si_to_unit(mm(10))
        support_disk_radius = railing_radius
        support_disk_depth = self.convert_si_to_unit(mm(20))

        # util functions
        float_is_zero = lambda f: 0.0001 >= f >= -0.0001
        collinear = lambda d0, d1: float_is_zero(d0.angle(d1))

        def add_support_on_point(point, railing_direction):
            """create a support arc and a disk based on the position and direction of the railing"""
            ortho_dir = (railing_direction.yx * V(1, -1)).to_3d().normalized()
            arc_center = point + ortho_dir * support_length
            support_points = [
                point,
                arc_center - ortho_dir * support_length * cos(pi / 4) + z_down * support_length * sin(pi / 4),
                arc_center + z_down * support_length,
            ]
            polyline = builder.polyline(support_points, closed=False, arc_points=[1])
            solid = builder.create_swept_disk_solid(polyline, support_radius)

            support_disk_circle = builder.circle(radius=support_disk_radius)

            angle = V(0, 1).angle_signed(ortho_dir.xy)
            y_extrusion_kwargs = builder.rotate_extrusion_kwargs_by_z(builder.extrude_kwargs("Y"), angle)
            support_disk = builder.extrude(
                support_disk_circle, support_disk_depth, position=support_points[-1], **y_extrusion_kwargs
            )
            return [solid, support_disk]

        def get_fillet_points(v0, v1, v2, radius):
            """get fillet points between edges v0v1 and v1v2"""
            dir1 = (v0 - v1).normalized()
            dir2 = (v2 - v1).normalized()
            edge_angle = dir1.angle(dir2)
            slide_distance = radius / tan(edge_angle / 2)

            fillet_v1co = v1 + (dir1 * slide_distance)
            fillet_v2co = v1 + (dir2 * slide_distance)

            normal = mathutils.geometry.normal([v0, v1, v2])
            center = mathutils.geometry.intersect_line_line(
                fillet_v1co, fillet_v1co + normal.cross(dir1), fillet_v2co, fillet_v2co + normal.cross(dir2)
            )[0]

            midpointco = center + ((fillet_v1co.lerp(fillet_v2co, 0.5) - center).normalized() * radius)
            return [fillet_v1co, midpointco, fillet_v2co]

        def add_arcs_on_turnings_points(base_points):
            """add 3 point fillet arcs on turning points of the railing path"""
            if len(base_points) < 3:
                return base_points

            # looking for turning points by checking non-collinear edges
            output_points = base_points[:1]
            prev_dir = (base_points[1] - base_points[0]).normalized()
            i = 1
            while i < len(base_points) - 1:
                cur_dir = (base_points[i + 1] - base_points[i]).normalized()

                if collinear(cur_dir, prev_dir):
                    output_points.append(base_points[i])
                else:
                    fillet_points = get_fillet_points(
                        base_points[i - 1], base_points[i], base_points[i + 1], railing_fillet_radius
                    )
                    output_points.extend(fillet_points)
                    arc_points.append(fillet_points[1])

                prev_dir = cur_dir
                i = i + 1

            if looped_path:
                output_points[0] = output_points[-1]
            else:
                output_points.append(base_points[-1])
            return output_points

        def create_supports_items(railing_coords, manual_supports=False):
            """create supports items based on the railing coordinates"""
            supports_items = []

            # simplified_coords is a list of points that form non-collinear edges
            simplified_coords = [railing_coords[0]]
            prev_dir = (railing_coords[1] - railing_coords[0]).normalized()

            # iterating over each edge of the railing path
            for i in range(1, len(railing_coords) - 1):
                cur_dir = (railing_coords[i + 1] - railing_coords[i]).normalized()

                if not collinear(cur_dir, prev_dir):
                    simplified_coords.append(railing_coords[i])
                    prev_dir = cur_dir

                # for manual supports each vertex on the railing path edge
                # will be a point for a support
                elif manual_supports:
                    supports_items.extend(add_support_on_point(point=railing_coords[i], railing_direction=cur_dir))

            simplified_coords.append(railing_coords[-1])

            if manual_supports:
                return supports_items

            # create automatic supports based on the support spacing
            for i in range(0, len(simplified_coords) - 1):
                v0, v1 = simplified_coords[i : i + 2]
                edge = v1 - v0
                length = edge.length
                edge_dir = edge.normalized()
                n_supports, support_offset = divmod(length, support_spacing)
                n_supports = int(n_supports) + 1
                support_offset /= 2

                start_position = v0 + support_offset * edge_dir
                for support_i in range(n_supports):
                    support_position = start_position + support_i * support_spacing * edge_dir
                    supports_items.extend(add_support_on_point(point=support_position, railing_direction=edge))

            return supports_items

        def add_cap(railing_coords, arc_points, start=False):
            """add handrail terminal cap"""
            railing_coords_for_cap = railing_coords[::-1] if start else railing_coords

            start_point = railing_coords_for_cap[-1]
            cap_dir = (railing_coords_for_cap[-1] - railing_coords_for_cap[-2]).to_3d().normalized()
            ortho_dir = (cap_dir.yx * V(1, -1)).to_3d().normalized()
            local_z_down = cap_dir.cross(ortho_dir)
            if start:
                ortho_dir = -ortho_dir

            arc_middle_point_cos = sin(radians(45))

            if cap_type in ("180", "TO_END_POST"):
                arc_point = start_point + cap_dir * terminal_radius + terminal_radius * local_z_down
                arc_points.append(arc_point)
                cap_coords = [arc_point, start_point + terminal_radius * 2 * local_z_down]

                if cap_type == "TO_END_POST":
                    end_point = railing_coords_for_cap[-2].copy()
                    end_point.z -= terminal_radius * 2
                    cap_coords.append(end_point)

            elif cap_type == "TO_WALL":
                arc_point = (
                    start_point
                    + cap_dir * clear_width * arc_middle_point_cos
                    + ortho_dir * clear_width * (1 - arc_middle_point_cos)
                )
                arc_points.append(arc_point)
                cap_coords = [arc_point, start_point + ortho_dir * clear_width + cap_dir * clear_width]

            elif cap_type == "TO_FLOOR":
                arc_point = (
                    start_point
                    + cap_dir * terminal_radius * arc_middle_point_cos
                    + z_down * terminal_radius * (1 - arc_middle_point_cos)
                )
                arc_points.append(arc_point)
                arc_end = start_point + cap_dir * terminal_radius + terminal_radius * z_down
                cap_coords = [
                    arc_point,
                    arc_end,
                    arc_end + z_down * (height - terminal_radius),
                ]

            elif cap_type == "TO_END_POST_AND_FLOOR":
                first_arc_end = start_point + cap_dir * terminal_radius + terminal_radius * local_z_down
                first_arc_coords = get_fillet_points(
                    start_point, start_point + cap_dir * terminal_radius, first_arc_end, terminal_radius
                )
                arc_points.append(first_arc_coords[1])

                end_point = railing_coords_for_cap[-2].copy()
                end_point.z -= height
                second_arc_coords = get_fillet_points(
                    first_arc_end, first_arc_end + local_z_down * terminal_radius, end_point, terminal_radius
                )
                arc_points.append(second_arc_coords[1])
                cap_coords = [start_point] + first_arc_coords + second_arc_coords + [end_point]

            railing_coords = railing_coords_for_cap + cap_coords

            if start:
                railing_coords = railing_coords[::-1]
            return railing_coords, arc_points

        # need to add first two points to the path
        # to create the turning arcs and supports on the last segment of the loop
        if looped_path:
            railing_coords += railing_coords[:2]

        items_3d.extend(create_supports_items(railing_coords, manual_supports=use_manual_supports))
        railing_coords = add_arcs_on_turnings_points(railing_coords)

        if not looped_path and cap_type != "NONE":
            railing_coords, arc_points = add_cap(railing_coords, arc_points, start=True)
            railing_coords, arc_points = add_cap(railing_coords, arc_points, start=False)

        railing_path = builder.polyline(
            railing_coords, closed=False, arc_points=[railing_coords.index(p) for p in arc_points]
        )
        railing_solid = builder.create_swept_disk_solid(railing_path, railing_radius)
        items_3d.append(railing_solid)
        representation = builder.get_representation(ifc_context, items=items_3d)
        return representation

    def convert_si_to_unit(self, value):
        return value / self.settings["unit_scale"]

    def path_si_to_units(self, path):
        """converts list of vectors from SI to ifc project units"""
        return [self.convert_si_to_unit(v) for v in path]
