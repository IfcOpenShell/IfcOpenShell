# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2020, 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import re
from collections.abc import Iterable
from math import sin
from typing import Literal, TypedDict, Union

import bmesh
import bpy
import ifcopenshell
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.unit
import ifcopenshell.util.unit as ifcunit
import numpy as np
import numpy.typing as npt
from mathutils import Vector

import bonsai.tool as tool
from bonsai.bim.module.structural.shader import DecorationShader


class MemberInfo(TypedDict):
    member: ifcopenshell.entity_instance
    activities: list[tuple[ifcopenshell.entity_instance, float]]


LoadConfigItem = TypedDict(
    "LoadConfigItem", {"pos": float, "descr": Literal["start", "end", "middle"], "load values": np.ndarray}
)


class DiscreteConfigItem(TypedDict):
    pos: float
    values: list[float]


ParsedLoad = TypedDict(
    "ParsedLoad",
    {
        "constant force": list[float],
        "quadratic force": list[float],
        "sinus force": list[float],
        "linear load configuration": list[list[LoadConfigItem]],
        "point load configuration": list[list[DiscreteConfigItem]],
    },
)


class LoadByDirection(TypedDict):
    constant: float
    quadratic: float
    sinus: float
    polyline: list[list[float]]


ProcessedLoad = TypedDict(
    "ProcessedLoad",
    {
        "linear loads": dict[str, LoadByDirection] | None,
        "max linear load": float,
        "discrete loads": list[list[DiscreteConfigItem]],
    },
)


def box_crosses_segments(
    left: float, low: float, width: float, height: float, segments: Iterable[tuple[Iterable, Iterable]]
) -> bool:
    """Whether a label's box, from (left, low) and of a width and height in 2D, touches any of the lines given as
    pairs of end points, so that labels can keep off arrows and arcs as well as each other"""
    right, high = left + width, low + height
    for (x1, y1), (x2, y2) in segments:
        if max(x1, x2) < left or min(x1, x2) > right or max(y1, y2) < low or min(y1, y2) > high:
            continue  # Nowhere near, which most lines are; quick to rule out, as this runs on every redraw.
        # Clip the line to the box (Liang-Barsky): any part left means it crosses the box.
        t0, t1 = 0.0, 1.0
        dx, dy = x2 - x1, y2 - y1
        for p, q in ((-dx, x1 - left), (dx, right - x1), (-dy, y1 - low), (dy, high - y1)):
            if p == 0:
                if q < 0:
                    break  # Parallel to this edge and outside it.
                continue
            t = q / p
            if p < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
            if t0 > t1:
                break
        else:
            return True
    return False


def get_plain_symbol(symbol: str) -> str:
    """A symbol written F_{x1}, as reports set it, in plain text with Unicode subscripts where there are some, as
    F₁ or Fₓ₁; Unicode has no subscript z, so it stays as it is"""
    lower = str.maketrans("0123456789x", "₀₁₂₃₄₅₆₇₈₉ₓ")
    return re.sub(r"_\{([^}]*)\}", lambda m: m[1].translate(lower), symbol)


def segments_cross(p1: Iterable, p2: Iterable, q1: Iterable, q2: Iterable) -> bool:
    """Whether two lines in a plane, given by their end points as (x, y), cross or touch"""

    def turn(a: Iterable, b: Iterable, c: Iterable) -> float:
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    d1, d2, d3, d4 = turn(q1, q2, p1), turn(q1, q2, p2), turn(p1, p2, q1), turn(p1, p2, q2)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)) and 0 not in (d1, d2, d3, d4):
        return True
    on = lambda a, b, c, d: (
        d == 0 and min(a[0], b[0]) <= c[0] <= max(a[0], b[0]) and min(a[1], b[1]) <= c[1] <= max(a[1], b[1])
    )
    return on(q1, q2, p1, d1) or on(q1, q2, p2, d2) or on(p1, p2, q1, d3) or on(p1, p2, q2, d4)


class ShaderInfo:
    # Values of a load being edited, by load id, shown in place of its own until the edit is confirmed or cancelled.
    preview: dict[int, dict[str, Union[float, None]]] = {}
    # A point's axes being edited, and the slope they are set by if any, by its id, shown in place of its own likewise.
    preview_axes: dict[int, tuple[np.ndarray, Union[tuple[float, float], None]]] = {}
    # The eighth Edit Resultant measures a resultant's angle in, by its item's id, shown in place of the chosen one.
    preview_resultant_eighths: dict[int, Union[str, None]] = {}

    def __init__(self, load_group: Union[ifcopenshell.entity_instance, None] = None) -> None:
        """
        :param load_group: The load group to draw, rather than the one chosen to show, as for a report.
        """
        self.load_group = load_group
        self.is_empty = True
        self.shader = DecorationShader()
        self.curve_members: dict[str, MemberInfo] = {}
        self.point_members: dict[str, MemberInfo] = {}
        self.surface_members: dict[str, MemberInfo] = {}
        self.text_info = []
        self.info = []
        self.pickables = []
        self.force_unit = ""
        self.moment_unit = ""
        self.length_unit = ""
        # The scale forces are drawn to while moments are taken about a point, to keep them in proportion.
        self.moment_force_scale = None
        self.linear_force_unit = ""
        self.linear_moment_unit = ""
        self.planar_force_unit = ""

    def update(self) -> None:
        self.info = []
        self.text_info = []
        # Arrows that stand for one applied load, so that they can be picked in the viewport to edit it.
        self.pickables = []
        self.tagging_object = None
        self.curve_members = {}
        self.point_members = {}
        self.surface_members = {}
        self.get_force_units()
        self.get_structural_elements_and_activities()
        self.moment_force_scale = self.get_moment_force_scale()
        self.get_linear_loads()
        self.get_point_loads()
        self.get_planar_loads()
        self.get_moments()
        self.tag_new_entries(None)
        if len(self.info):
            self.is_empty = False

    def get_force_units(self) -> None:
        def get_unit_symbol(unit: ifcopenshell.entity_instance) -> str:
            prefix_symbols = {
                "EXA": "E",
                "PETA": "P",
                "TERA": "T",
                "GIGA": "G",
                "MEGA": "M",
                "KILO": "k",
                "HECTO": "h",
                "DECA": "da",
                "DECI": "d",
                "CENTI": "c",
                "MILLI": "m",
                "MICRO": "μ",
                "NANO": "n",
                "PICO": "p",
                "FEMTO": "f",
                "ATTO": "a",
            }

            unit_symbols = {
                # si units
                "CUBIC_METRE": "m3",
                "GRAM": "g",
                "SECOND": "s",
                "SQUARE_METRE": "m2",
                "METRE": "m",
                "NEWTON": "N",
                "PASCAL": "Pa",
                # conversion based units
                "pound-force": "lbf",
                "pound-force per square inch": "psi",
                "thou": "th",
                "inch": "in",
                "foot": "ft",
                "yard": "yd",
                "mile": "mi",
                "square thou": "th2",
                "square inch": "in2",
                "square foot": "ft2",
                "square yard": "yd2",
                "acre": "ac",
                "square mile": "mi2",
                "cubic thou": "th3",
                "cubic inch": "in3",
                "cubic foot": "ft3",
                "cubic yard": "yd3",
                "cubic mile": "mi3",
                "litre": "L",
                "fluid ounce UK": "fl oz",
                "fluid ounce US": "fl oz",
                "pint UK": "pt",
                "pint US": "pt",
                "gallon UK": "gal",
                "gallon US": "gal",
                "degree": "°",
                "ounce": "oz",
                "pound": "lb",
                "ton UK": "ton",
                "ton US": "ton",
                "lbf": "lbf",
                "kip": "kip",
                "psi": "psi",
                "ksi": "ksi",
                "minute": "min",
                "hour": "hr",
                "day": "day",
                "btu": "btu",
                "fahrenheit": "°F",
            }
            symbol = ""
            if unit.is_a("IfcSIUnit"):
                symbol += prefix_symbols.get(unit.Prefix, "")
            symbol += unit_symbols.get(unit.Name.replace("METER", "METRE"), "?")
            return symbol

        # Only units assigned to the project apply. Missing ones fall back to SI, as ifcopenshell.util.unit assumes.
        ifc_file = tool.Ifc.get()
        project_units = {
            t: ifcunit.get_project_unit(ifc_file, t)
            for t in ("FORCEUNIT", "LENGTHUNIT", "LINEARFORCEUNIT", "LINEARMOMENTUNIT", "PLANARFORCEUNIT")
        }
        linear_force_units = [u for u in [project_units["LINEARFORCEUNIT"]] if u]
        linear_moment_units = [u for u in [project_units["LINEARMOMENTUNIT"]] if u]
        planar_force_units = [u for u in [project_units["PLANARFORCEUNIT"]] if u]

        force_unit = project_units["FORCEUNIT"]
        self.force_unit = ifcunit.get_unit_symbol(force_unit) if force_unit else "N"

        length_unit = project_units["LENGTHUNIT"]
        length_unit = ifcunit.get_unit_symbol(length_unit) if length_unit else "m"
        self.moment_unit = self.force_unit + "." + length_unit
        self.length_unit = length_unit

        # Derived units missing from the file are composed from the force and length units.
        first = self.force_unit
        second = length_unit
        for e in linear_force_units[0].Elements if linear_force_units else ():
            if e.Unit.UnitType == "FORCEUNIT":
                first = ifcunit.get_unit_symbol(e.Unit)
            if e.Unit.UnitType == "LENGTHUNIT":
                second = ifcunit.get_unit_symbol(e.Unit)
        self.linear_force_unit = first + "/" + second

        first = self.force_unit
        second = length_unit
        for e in linear_moment_units[0].Elements if linear_moment_units else ():
            if e.Unit.UnitType == "FORCEUNIT":
                first = ifcunit.get_unit_symbol(e.Unit)
            if e.Unit.UnitType == "LENGTHUNIT":
                second = ifcunit.get_unit_symbol(e.Unit)
        self.linear_moment_unit = first + "." + second + "/" + second

        first = self.force_unit
        second = length_unit + "2"
        for e in planar_force_units[0].Elements if planar_force_units else ():
            if e.Unit.UnitType == "FORCEUNIT":
                first = ifcunit.get_unit_symbol(e.Unit)
            if e.Unit.UnitType == "LENGTHUNIT":
                second = ifcunit.get_unit_symbol(e.Unit) + "2"
            if e.Unit.UnitType == "AREAUNIT":
                second = ifcunit.get_unit_symbol(e.Unit)
        self.planar_force_unit = first + "/" + second

    def get_structural_elements_and_activities(self) -> None:
        """fills self.point_members, self.curve_members and self.surface_members dictionaries"""

        def populate_members_dict(
            dict_name: Literal["point_members", "curve_members", "surface_members"],
            element: ifcopenshell.entity_instance,
            activity: ifcopenshell.entity_instance,
            factor: float,
        ) -> None:
            """
            fills self.point_members, self.curve_members and self.surface_members dictionaries
            thoses dicts will contain the structural member global id as key and a second dict as value
            the second dict contais two keys, as follow:
            {
                "member": the strucutral member itself
                "activities: list[(activity, factor)] for each activity applied to the member
            }
            dict_name: "point_members", "curve_members" or "surface_members"
            element: IfcStructuralMember
            activity: IfcStructuralActivity
            factor: float to multiply the loads values in the structural activity
            """
            dic = getattr(self, dict_name, None)
            if dic is None:
                return
            member = dic.get(element.GlobalId)
            if member is None:
                dic.update({element.GlobalId: {"member": element, "activities": [(activity, factor)]}})
            else:
                member["activities"].append((activity, factor))

        def recursive_subgroups(
            groups: list[ifcopenshell.entity_instance],
            rec_limit: int,
            activity_type: Literal["Action", "External Reaction"],
            factor: float = 1,
        ) -> None:
            """
            Recursively fills self.point_members, self.curve_members and self.surface_members dictionaries
            with the structural members to wich the activities in the load group and its subgroups are applied
            it also creates a list with all the activities applied to that member that are in the same
            load group or subgroup (see populate_members_dict description)

            groups: list of Ifc load case, load group or load combination
            rec_limit: maximum number of recursions
            activity_type: "Action" or "External Reaction"
            factor: the factor applied to the group, default = 1
                    this factor will be multiplied by the group coefficient and the factor of a
                    IfcRelAssignsToGroupByFactor relationship of subgroups in load combinations

            """
            if rec_limit == 0 or len(groups) == 0:
                return None
            for group in groups:
                subgorups = []
                activities = []
                relationship = [rel for rel in group.IsGroupedBy]
                coef = getattr(group, "Coefficient", 1.0)
                group_coef = coef if coef is not None else 1.0
                rel_factor = 1.0

                for rel in relationship:
                    if rel.is_a("IfcRelAssignsToGroupByFactor"):
                        rel_factor = rel.Factor if rel.Factor is not None else 1.0
                    objects = rel.RelatedObjects
                    subgorups = [sg for sg in objects if sg.is_a("IfcStructuralLoadGroup")]
                    activities = [a for a in objects if a.is_a("IfcStructuralActivity")]
                    factor = factor * group_coef * rel_factor
                    for activity in activities:
                        if len(activity.AssignedToStructuralItem):
                            element = activity.AssignedToStructuralItem[0].RelatingElement
                            if element is not None:
                                if activity_type == "Action":
                                    if element.is_a("IfcStructuralCurveMember"):
                                        populate_members_dict("curve_members", element, activity, factor)
                                    elif element.is_a("IfcStructuralPointConnection"):
                                        populate_members_dict("point_members", element, activity, factor)
                                    elif element.is_a("IfcStructuralSurfaceMember"):
                                        populate_members_dict("surface_members", element, activity, factor)

                                elif (
                                    activity_type == "External Reaction"
                                    and getattr(element, "AppliedCondition", None) is not None
                                ):
                                    if element.is_a("IfcStructuralCurveMember"):
                                        populate_members_dict("curve_members", element, activity, factor)
                                    elif element.is_a("IfcStructuralPointConnection"):
                                        populate_members_dict("point_members", element, activity, factor)
                                    elif element.is_a("IfcStructuralSurfaceMember"):
                                        populate_members_dict("surface_members", element, activity, factor)
                    recursive_subgroups(subgorups, rec_limit - 1, activity_type, factor=factor)

        props = tool.Structural.get_structural_props()
        file = tool.Ifc.get()
        try:
            group = self.load_group or file.by_id(int(props.load_group_to_show))
        except (ValueError, RuntimeError):
            return  # No load group is chosen, or the chosen one was removed.
        if group.is_a("IfcStructuralLoadGroup"):
            recursive_subgroups([group], 10, props.activity_type)

    def tag_new_entries(self, obj: Union[bpy.types.Object, None]) -> None:
        """Mark the drawing data added so far without an item as belonging to the item just drawn.

        Each load type draws one structural item at a time, calling this with the next item before
        drawing it, so that a load's arrows and values hide with their item.
        """
        if self.tagging_object is not None:
            for entry in self.info + self.text_info:
                entry.setdefault("object", self.tagging_object)
        self.tagging_object = obj.name if obj else None

    def get_planar_loads(self) -> None:
        """get the necessary information to render the planar load representation in 3D and its text information"""

        list_of_surfaces = self.surface_members
        shader = self.shader.new("PLANAR LOAD")
        maximum = 0
        for value in list_of_surfaces.values():
            surf = value["member"]
            self.tag_new_entries(tool.Ifc.get_object(surf))
            activity_list = value["activities"]
            if len(activity_list) == 0:
                continue
            rotation = self.get_surface_member_rotation(surf)
            values = self.get_planar_loads_values(activity_list, rotation)
            if maximum == 0:
                maximum = max([abs(float(i)) for i in values])
                if maximum == 0:
                    continue
            props = tool.Structural.get_structural_props()
            reference_frame = props.reference_frame
            orientation = np.eye(3)
            if reference_frame == "LOCAL_COORDS":
                orientation = rotation
            blender_object: bpy.types.Object = tool.Ifc.get_object_by_identifier(getattr(surf, "GlobalId", None))
            mat = blender_object.matrix_world
            mesh: bpy.types.Mesh = blender_object.data

            positions = []
            indices = []
            coord = []
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bmesh.ops.triangulate(bm, faces=bm.faces)
            bm.edges.ensure_lookup_table()
            bm.verts.ensure_lookup_table()
            bm.faces.ensure_lookup_table()

            for v in bm.verts:
                p1 = np.array(mat @ v.co)
                positions.append(p1)
                p2 = p1 - (orientation @ values) * 0.2 / maximum
                positions.append(p2)
                coord.append((float(p1[0] + p1[1]), 0, 1))
                coord.append((float(p1[0] + p1[1]), 1, 1))
            for e in bm.edges:
                if len(e.link_faces) > 1:
                    continue
                indices.append((2 * e.verts[0].index, 2 * e.verts[0].index + 1, 2 * e.verts[1].index))
                indices.append((2 * e.verts[0].index + 1, 2 * e.verts[1].index, 2 * e.verts[1].index + 1))
            for p in bm.faces:
                indices.append((2 * p.verts[0].index + 1, 2 * p.verts[1].index + 1, 2 * p.verts[2].index + 1))
            bmesh.ops.dissolve_limit(bm, angle_limit=0.01, verts=bm.verts, edges=bm.edges)
            bm.faces.ensure_lookup_table()
            center = bm.faces[0].calc_center_bounds()

            self.text_info.append(
                {
                    "position": mat @ center - Vector((orientation @ values) * 0.2 / maximum),
                    "text": f"{values[2]:.5f} {self.planar_force_unit}",
                }
            )

            self.info.append(
                {
                    "shader": shader,
                    "args": {"position": positions, "coord": coord},
                    "indices": indices,
                    "uniforms": [["color", (0.2, 0, 1, 1)], ["spacing", 0.2]],
                }
            )

    def get_planar_loads_values(
        self, activity_list: list[tuple[ifcopenshell.entity_instance, float]], element_rotation_matrix: np.ndarray
    ) -> np.ndarray:
        """
        returns a numpy array with the sum of the values of structural activities
        applied loads in each direction, multiplied by the factors in load combinations
        """
        values = np.zeros(3)
        for item in activity_list:
            activity = item[0]
            factor = item[1]
            load = activity.AppliedLoad
            temp = np.zeros(3)
            if load is not None and load.is_a("IfcStructuralLoadPlanarForce"):
                temp[0] = load.PlanarForceX if load.PlanarForceX is not None else 0
                temp[1] = load.PlanarForceY if load.PlanarForceY is not None else 0
                temp[2] = load.PlanarForceZ if load.PlanarForceZ is not None else 0
            temp = temp * factor
            transform = self.get_activity_transform_matrix(activity, element_rotation_matrix)
            values += transform @ temp
        return values

    def get_surface_member_rotation(self, surface_member: ifcopenshell.entity_instance) -> np.ndarray:
        """returns the rotation matrix of a structural surface member"""
        representation = ifcopenshell.util.representation.get_representation(surface_member, "Model")
        repr_item = representation.Items[0]
        placement = ifcopenshell.util.placement.get_placement(repr_item.FaceSurface.Position)
        rotation = placement[0:3, 0:3]
        return rotation

    def get_point_connection_rotation(self, point_connection: ifcopenshell.entity_instance) -> np.ndarray:
        """returns the rotation matrix of a structural point connection"""
        if point_connection.ConditionCoordinateSystem is not None:
            placement = ifcopenshell.util.placement.get_placement(point_connection.ConditionCoordinateSystem)
        else:
            placement = np.eye(4)
        rotation = placement[0:3, 0:3]
        return rotation

    def get_curve_member_rotation(self, curve_member: ifcopenshell.entity_instance) -> np.ndarray:
        """returns the rotation matrix of a structural surface member"""
        z = curve_member.Axis.DirectionRatios
        edge = curve_member.Representation.Representations[0].Items[0]
        origin = edge.EdgeStart.VertexGeometry.Coordinates
        end = edge.EdgeEnd.VertexGeometry.Coordinates
        x = [c2 - c1 for c1, c2 in zip(origin, end)]
        placement = ifcopenshell.util.placement.a2p(origin, z, x)
        rotation = placement[0:3, 0:3]
        return rotation

    def get_activity_transform_matrix(
        self, activity: ifcopenshell.entity_instance, element_rotation_matrix: np.ndarray
    ) -> np.ndarray:
        "provides the transformation matrix to convert between reference frames"
        global_or_local = activity.GlobalOrLocal
        props = tool.Structural.get_structural_props()
        reference_frame = props.reference_frame
        transform_matrix = np.eye(3)
        if reference_frame == "LOCAL_COORDS" and global_or_local != reference_frame:
            transform_matrix = np.linalg.inv(element_rotation_matrix)
        elif reference_frame == "GLOBAL_COORDS" and global_or_local != reference_frame:
            transform_matrix = element_rotation_matrix
        return transform_matrix

    def get_point_loads(self) -> None:
        """get the necessary information to render the point load representation in 3D and its text information"""

        list_of_point_connections = self.point_members
        for value in list_of_point_connections.values():
            conn = value["member"]
            self.tag_new_entries(tool.Ifc.get_object(conn))
            activity_list = value["activities"]
            if len(activity_list) == 0:
                continue
            blender_object = tool.Ifc.get_object_by_identifier(getattr(conn, "GlobalId", None))
            if blender_object.type == "MESH":
                conn_location = blender_object.matrix_world @ blender_object.data.vertices[0].co
                rotation, slope = self.preview_axes.get(conn.id(), (None, None))
                if rotation is None:
                    rotation, slope = self.get_point_connection_rotation(conn), tool.Structural.get_axes_slope(conn)
                self.get_point_force_args(activity_list, conn_location, rotation, slope)
                # Moments keep their own symbol; forces are drawn above.
                loads = self.get_point_loads_values(activity_list, rotation)
                self.get_point_moment_args(loads[3:], conn_location, rotation)

    def get_moment_forces(self) -> list[tuple[ifcopenshell.entity_instance, int, np.ndarray, np.ndarray]]:
        """Each point force drawn, as its point, its applied load's id, its point's location and its force in global
        terms, by point name and then tip-to-tail order, as moments number them"""
        forces = []
        for value in sorted(self.point_members.values(), key=lambda v: (v["member"].Name or "", v["member"].id())):
            point = value["member"]
            obj = tool.Ifc.get_object(point)
            if not obj or obj.type != "MESH" or not obj.data.vertices:
                continue
            location = np.array(obj.matrix_world @ obj.data.vertices[0].co, dtype=float)
            rotation, _ = self.preview_axes.get(point.id(), (None, None))
            rotation = self.get_point_connection_rotation(point) if rotation is None else rotation
            items = sorted(value["activities"], key=lambda item: tool.Structural.get_draw_order_key(item[0]))
            for item in items:
                force = self.get_point_loads_values([item], rotation)[:3]
                if np.linalg.norm(force):
                    forces.append((point, item[0].id(), location, force))
        return forces

    def get_moment_centre(
        self,
    ) -> tuple[
        Union[ifcopenshell.entity_instance, None],
        Union[bpy.types.Object, None],
        Union[np.ndarray, None],
        Union[ifcopenshell.entity_instance, None],
    ]:
        """The point moments are taken about for the load case drawn, its object and its location, and the load
        case, if one is"""
        props = tool.Structural.get_structural_props()
        try:
            group = self.load_group or tool.Ifc.get().by_id(int(props.load_group_to_show))
        except (ValueError, RuntimeError):
            return None, None, None, None
        if not group.is_a("IfcStructuralLoadGroup") or not (centre := tool.Structural.get_moment_centre(group)):
            return None, None, None, None
        if not (obj := tool.Ifc.get_object(centre)) or obj.type != "MESH" or not obj.data.vertices:
            return None, None, None, None
        # In double precision: Blender's coordinates are single, which its shader uniforms do not take.
        return centre, obj, np.array(obj.matrix_world @ obj.data.vertices[0].co, dtype=float), group

    def get_moment_force_scale(self) -> Union[float, None]:
        """With moments taken about a point, the scale forces are drawn to, so that they keep in proportion with
        the distances between points rather than each point's diagram having its own: the largest force reaches
        0.4 of the way to the furthest loaded point. None without a moment centre."""
        centre, _, at, _ = self.get_moment_centre()
        if not centre or not (forces := self.get_moment_forces()):
            return None
        reach = float(max(np.linalg.norm(location - at) for _, _, location, _ in forces))
        largest = float(max(np.linalg.norm(force) for _, _, _, force in forces))
        return 0.4 * reach / largest if reach and largest else None

    def get_moments(self) -> None:
        """Draw the moment of each point force about the point chosen as the moment centre for the load case shown:
        its line of action, its moment arm from the centre, and their sum as a curved arrow at the centre.

        Moments are counter-clockwise positive as the X-Z plane is seen from -Y, as statics texts take them.
        Moments applied as loads are left out: they are in the project's torque unit, not force times length.
        """
        props = tool.Structural.get_structural_props()
        ifc_file = tool.Ifc.get()
        centre, obj, at, group = self.get_moment_centre()
        if not centre:
            return
        forces = self.get_moment_forces()
        if not forces:
            return
        first, first_text = len(self.info), len(self.text_info)
        length_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)  # Metres per project length unit.
        # Sized to what is drawn, as a point's diagram is to its longest arrow.
        reach = float(max(np.linalg.norm(location - at) for _, _, location, _ in forces))
        size = 0.3 * reach if reach else 1.0
        colors = {t["force_of"]: t["color"] for t in self.text_info if t.get("force_of")}
        decimals = props.force_decimals
        total = 0.0
        starts = []  # Where each force's drawing starts, to hide it with its point.
        for i, (point, activity, location, force) in enumerate(forces, 1):
            starts.append((len(self.info), len(self.text_info), point, activity))
            moment, arm, foot = tool.Structural.get_moment(at, location, force)
            moment /= length_scale  # Its distances in the project's length unit, as its forces are in theirs.
            arm /= length_scale
            total += moment
            color = colors.get(activity, (1, 1, 1, 1))
            symbol = get_plain_symbol(f"M_{{{i}}}")
            along = np.array((force[0], 0.0, force[2]))
            if not np.linalg.norm(along) or arm * length_scale < 1e-9 * max(reach, 1e-9):
                text = f"{symbol} = 0: its line of action passes through A"
                self.text_info.append(
                    {"position": location, "text": text, "color": color, "away": np.array((0, 0, 1.0))}
                )
                continue
            along /= np.linalg.norm(along)
            # Its line of action, on to the foot of its arm, then the arm, square to it, from the centre.
            if np.linalg.norm(foot - location) > 1e-9 * reach:
                self.add_dashed_line(location, foot, size, color)
            self.add_dashed_line(at, foot, size, color)
            towards = (at - foot) / np.linalg.norm(at - foot)
            corner = 0.06 * size
            if np.linalg.norm(at - foot) > 3 * corner:
                side = along if np.dot(location - foot, along) >= 0 else -along
                a, b = foot + towards * corner, foot + side * corner
                self.add_dashed_line(a, a + side * corner, size, color, dashed=False)
                self.add_dashed_line(b, b + towards * corner, size, color, dashed=False)
            turn = "CCW" if moment > 0 else "CW"  # The viewport's font has no turning arrows.
            # The arm's length, then its moment beneath it: labels placed later move clear of earlier ones, away
            # from the arm, which is down, or across for a level line of action.
            away = -along if along[2] > 0 else along
            for text in (
                f"{get_plain_symbol(f'd_{{{i}}}')} = {arm:.2f} {self.length_unit}",
                f"{symbol} = {abs(moment):.{decimals}f} {self.moment_unit} {turn}",
            ):
                self.text_info.append(
                    {"position": (at + foot) / 2, "text": text, "color": color, "away": away, "focus": "arm"}
                )
            self.add_moment_triangle(i, at, location, foot, size, color, length_scale)
        # Each force's moment hides with its point as its force does, and all of them with the centre.
        ends = [(info, text) for info, text, _, _ in starts[1:]] + [(len(self.info), len(self.text_info))]
        for (info, text, point, activity), (info_end, text_end) in zip(starts, ends):
            point_obj = tool.Ifc.get_object(point)
            for entry in self.info[info:info_end] + self.text_info[text:text_end]:
                entry["visible_with"] = (obj.name, point_obj.name) if point_obj else (obj.name,)
            # Hovered, its lines and labels highlight together; clicked, they edit where A is from its point.
            texts = self.text_info[text:text_end]
            self.add_moment_pickable(info, info_end, texts, group.id(), point.id(), activity)
        self.add_moment_arrow(at, total, size, "ΣM_A" if len(forces) > 1 else "M_A", group.id())
        if self.load_group is not None:
            # A report's diagram stands alone, so it also draws what the viewport has around it.
            self.add_moment_context(centre, at, forces, size, reach, colors)
        for entry in self.info[first:] + self.text_info[first_text:]:
            entry["object"] = f"{obj.name} moments"  # Kept apart from the centre's own loads, as its own diagram.
            entry.setdefault("visible_with", (obj.name,))
        for text in self.text_info[first_text:]:
            text["label_scale"] = 1.4  # Sized as the force diagrams drawn with it, 0.4 of the distances to 0.3.

    def add_moment_context(
        self,
        centre: ifcopenshell.entity_instance,
        at: np.ndarray,
        forces: list[tuple[ifcopenshell.entity_instance, int, np.ndarray, np.ndarray]],
        size: float,
        reach: float,
        colors: dict[int, tuple],
    ) -> None:
        """Draw, for a report's moment diagram, the members along the points, each point's name, and each force at
        its point, to a scale that keeps them in proportion with the distances, named as the moments number them"""
        points = {point.id(): (point, location) for point, _, location, _ in forces}
        points[centre.id()] = (centre, at)
        gray = (0.6, 0.6, 0.6, 1)
        for member in tool.Ifc.get().by_type("IfcStructuralCurveMember"):
            obj = tool.Ifc.get_object(member)
            if not obj or obj.type != "MESH":
                continue
            connected = {rel.RelatedStructuralConnection.id() for rel in member.ConnectedBy or []}
            vertices = [np.array(obj.matrix_world @ v.co, dtype=float) for v in obj.data.vertices]
            for edge in obj.data.edges:
                a, b = (vertices[i] for i in edge.vertices)
                # Along the points: connected to one, or passing through one, as a beam drawn to its points is.
                if not connected & points.keys() and not any(
                    self.is_on_segment(location, a, b, reach) for _, location in points.values()
                ):
                    continue
                self.add_dashed_line(a, b, size, gray, dashed=False)
        for point, location in points.values():
            name = point.Name or "Unnamed"
            text = "A" if point == centre and name == "A" else f"A: {name}" if point == centre else name
            self.text_info.append({"position": location, "text": text, "color": gray, "away": np.array((-1, 0, -1.0))})
        scale = self.moment_force_scale or 1.0 / max(np.linalg.norm(force) for _, _, _, force in forces)
        ifc_file = tool.Ifc.get()
        for i, (_, activity, location, force) in enumerate(forces, 1):
            arrow = force * scale
            push = tool.Structural.get_push(ifc_file.by_id(activity))
            tail, tip = (location - arrow, location) if push else (location, location + arrow)
            color = colors.get(activity, (1, 1, 1, 2))
            unit = self.force_unit
            self.add_force_arrow(
                tail,
                tip,
                color,
                f"{np.linalg.norm(force):.{tool.Structural.get_structural_props().force_decimals}f} {unit}",
                size,
                label_at_tail=push,
            )
            self.text_info[-1]["symbol"] = f"F_{{{i}}}"

    def is_on_segment(self, point: np.ndarray, a: np.ndarray, b: np.ndarray, reach: float) -> bool:
        """Whether a point lies on the line between a and b, within a small share of the distances drawn"""
        length = np.linalg.norm(b - a)
        if not length:
            return False
        t = float(np.dot(point - a, b - a)) / length**2
        return -1e-6 <= t <= 1 + 1e-6 and np.linalg.norm(a + t * (b - a) - point) <= 1e-3 * max(reach, length)

    def add_moment_triangle(
        self,
        i: int,
        at: np.ndarray,
        location: np.ndarray,
        foot: np.ndarray,
        size: float,
        color: tuple,
        length_scale: float,
    ) -> None:
        """Complete the right triangle a force's moment arm makes, as a text draws it to find the arm: r, from the
        centre to the force's point, labelled with its length, with its direction and slope from the point if
        angles and slopes are shown, the angle phi between r and the line of action at that point, so that
        d = r sin phi, and the angle alpha at the centre"""
        r = location - at
        if not np.linalg.norm(r):
            return
        self.add_dashed_line(at, location, size, color)
        if tool.Structural.get_structural_props().show_force_slopes:
            # Its slope, from the point to A, as Edit Moment Centre enters it, as a force's slope is shown; A brought
            # to the point's X-Z plane, as Blender's single precision can leave it a hair off it, which shows none.
            self.add_force_slope(location, np.array((at[0], location[1], at[2])), size, color)
        across = np.array((-r[2], 0.0, r[0])) / np.linalg.norm(r)
        if np.dot(foot - at, across) > 0:
            across = -across  # Labelled outside the triangle.
        self.text_info.append(
            {
                "position": (at + location) / 2,
                "text": f"{get_plain_symbol(f'r_{{{i}}}')} = {np.linalg.norm(r) / length_scale:.2f} {self.length_unit}",
                "color": color,
                "away": across,
                "focus": "distance",
            }
        )
        if tool.Structural.get_structural_props().show_force_angles:
            # r's direction from the point, as Edit Moment Centre enters it, measured as a force's angle is.
            first_text, reference_axes = len(self.text_info), {}
            self.add_force_angle(location, np.array((-r[0], 0.0, -r[2])), size, color, {}, reference_axes)
            self.add_reference_axes(reference_axes, size)
            for text in self.text_info[first_text:]:
                text["text"] = text["text"].replace("θ =", f"{get_plain_symbol(f'r_{{{i}}}')} at", 1)
        # The triangle's other two angles: phi at the point, between r and the line of action, and alpha at the
        # centre, between r and the arm, 90 degrees less phi.
        if np.linalg.norm(foot - location) < 1e-9 * np.linalg.norm(r):
            return  # The line of action is square to r: phi is 90 degrees, shown by the arm's corner.
        self.add_angle_between(location, at, foot, size, color, get_plain_symbol(f"φ_{{{i}}}"), "phi")
        self.add_angle_between(at, location, foot, size, color, get_plain_symbol(f"α_{{{i}}}"), "alpha")

    def add_angle_between(
        self,
        vertex: np.ndarray,
        first: np.ndarray,
        second: np.ndarray,
        size: float,
        color: tuple,
        symbol: str,
        focus: str = "",
    ) -> None:
        """Mark the angle at a vertex between the lines to two points, in the X-Z plane, the acute way round, as an
        arc labelled with its value, if it is not too small to read"""
        one, other = first - vertex, second - vertex
        if not np.linalg.norm(one) or not np.linalg.norm(other):
            return
        start = np.arctan2(one[2], one[0])
        sweep = (np.arctan2(other[2], other[0]) - start + np.pi) % (2 * np.pi) - np.pi  # The shorter way round.
        angle = abs(np.degrees(sweep))
        if angle < 0.5:
            return  # Along one line: no angle to draw.
        radius = min(0.15 * size, 0.4 * np.linalg.norm(one), 0.4 * np.linalg.norm(other))
        angles = start + np.linspace(0, sweep, max(4, int(angle / 5)) + 1)
        arc = [vertex + radius * np.array((np.cos(a), 0.0, np.sin(a))) for a in angles]
        for a, b in zip(arc, arc[1:]):
            self.add_dashed_line(a, b, size, color, dashed=False)
        middle = start + sweep / 2
        outward = np.array((np.cos(middle), 0.0, np.sin(middle)))
        decimals = tool.Structural.get_structural_props().angle_decimals
        self.text_info.append(
            {
                "position": vertex + radius * outward,
                "text": f"{symbol} = {angle:.{decimals}f}°",
                "color": color,
                "away": outward,
                "focus": focus,
            }
        )

    def add_moment_arrow(self, at: np.ndarray, moment: float, size: float, symbol: str, load_case: int) -> None:
        """A curved arrow round a point turning the way a moment does, labelled with its value, which can be
        clicked to edit where the point is, for the load case taking moments about it"""
        color = (1, 1, 1, 2)
        decimals = tool.Structural.get_structural_props().force_decimals
        first = len(self.info)
        if abs(moment) < 10 ** -(decimals + 1):
            text = f"{symbol} = 0"
        else:
            text = f"{symbol} = {abs(moment):.{decimals}f} {self.moment_unit} {'CCW' if moment > 0 else 'CW'}"
            radius, sweep = 0.35 * size, (1 if moment > 0 else -1) * np.radians(270)
            angles = np.radians(-45) + np.linspace(0, sweep, 28)
            arc = [at + radius * np.array((np.cos(a), 0.0, np.sin(a))) for a in angles]
            for a, b in zip(arc[:-2], arc[1:-1]):
                self.add_dashed_line(a, b, size, color, dashed=False)
            self.add_force_arrow(arc[-3], arc[-1], color, "", size)
            self.text_info.pop()  # Its head only; the label is the moment's, above.
        self.text_info.append(
            {
                "position": at + np.array((0, 0, 0.35 * size)),
                "text": text,
                "color": color,
                "away": np.array((0, 0, 1.0)),
            }
        )
        if tool.Structural.get_resultant_moment(tool.Ifc.get().by_id(load_case)) is not None:
            self.text_info[-1]["text"] += " 🔒"  # Kept: forces changing re-solve the unknown to keep it.
        self.add_moment_pickable(first, len(self.info), self.text_info[-1:], load_case)
        self.pickables[-1]["moment_resultant"] = True  # Clicked, it edits the sum, as a resultant's value does.

    def add_moment_pickable(
        self,
        first: int,
        end: int,
        texts: list[dict],
        load_case: int,
        point: Union[int, None] = None,
        activity: Union[int, None] = None,
    ) -> None:
        """Make the moment lines drawn from first to end, and their labels, one pickable, as a force's arrow is:
        hovered anywhere along them, all of it highlights; clicked, it edits where the moment centre is, from the
        point given if any"""
        lines = [
            (primitive["start"], primitive["end"])
            if primitive["type"] == "LINE"
            else (primitive["tail"], primitive["tip"])
            for entry in self.info[first:end]
            if (primitive := entry.get("primitive"))
        ]
        pickable = {"activity": 0, "moment_of": load_case, "moment_from": point or 0, "anywhere": True}
        pickable["moment_activity"] = activity or 0
        if lines:
            pickable |= {"tail": lines[0][0], "tip": lines[0][1], "segments": lines, "info": first}
            pickable["whole"] = list(range(first, end))
        else:
            at = texts[0]["position"] if texts else np.zeros(3)  # Where dialogs keep clear of, as for R = 0.
            pickable |= {"tail": at, "tip": at, "info": None, "label_only": True}
        self.pickables.append(pickable)
        for text in texts:
            # A label that stands for a value highlights on its own, and opens the dialog with it ready to type.
            text["pickable"], text["part"] = len(self.pickables) - 1, text.get("focus") or "arrow"

    def get_point_force_args(
        self,
        activity_list: list[tuple[ifcopenshell.entity_instance, float]],
        location: Vector,
        rotation: np.ndarray,
        slope: Union[tuple[float, float], None] = None,
    ) -> None:
        """Draw the point forces applied at a point, and its own axes, set by slope if given"""
        # In their set draw order, else in the order they were applied.
        items = sorted(activity_list, key=lambda item: tool.Structural.get_draw_order_key(item[0]))
        forces = [self.get_point_loads_values([item], rotation)[:3] for item in items]
        self.draw_point_forces(forces, location, rotation, [item[0].id() for item in items], slope)

    def draw_point_forces(
        self,
        forces: list[np.ndarray],
        location: Vector,
        rotation: np.ndarray,
        activities: Union[list[int], None] = None,
        slope: Union[tuple[float, float], None] = None,
    ) -> None:
        """Draw point forces at a point from the point outwards, to scale, as chosen by force_display:
        the components or resultant of their sum, or each force added by the parallelogram law or tip to tail.

        forces: the X, Y and Z components of each force, in the reference frame being shown
        activities: the id of the activity applying each force, if any
        """
        props = tool.Structural.get_structural_props()
        location = np.array(location)
        first = len(self.info)  # This point's drawing starts here, which its axes reach across.
        self.point_first = first  # And which its slope triangles keep clear of.
        first_text = len(self.text_info)
        # Forces are numbered as they are drawn, tip to tail, as calculations number them.
        numbers = {activity: i for i, activity in enumerate(activities or [], 1) if activity}
        if props.reference_frame == "LOCAL_COORDS":
            forces = [rotation @ force for force in forces]
        kept = [
            (force, activity)
            for force, activity in zip(forces, activities or [0] * len(forces))
            if np.linalg.norm(force)
        ]
        if not kept:
            return
        forces = [force for force, _ in kept]
        activities = [activity for _, activity in kept]
        # Arrows can be picked to edit their load only when they stand for one applied load.
        single = activities[0] if len(activities) == 1 else 0
        resultant = sum(forces)
        resultant_marks = self.get_resultant_marks(activities)

        # All forces share one scale so that their lengths compare, as in a graphical solution.
        longest = max(np.linalg.norm(resultant), *(np.linalg.norm(force) for force in forces))
        # Forces in equilibrium leave only rounding noise, whose direction means nothing, so no resultant is drawn.
        in_equilibrium = np.linalg.norm(resultant) <= 1e-9 * longest
        if props.force_scale:
            scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get()) / props.force_scale
        elif self.moment_force_scale:
            scale = self.moment_force_scale  # In proportion with the distances moments are taken over.
        else:
            scale = 2 / longest
        # Arrowheads, shafts and dashes are sized to the longest arrow, so they read the same at any scale.
        size = longest * scale

        # Components lie on the axes, so they get no angle.
        axes = rotation if props.reference_frame == "LOCAL_COORDS" else np.eye(3)
        values = axes.T @ resultant
        axis_colors = [(1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1)]
        components = [
            (values[j] * axes[:, j], axis_colors[j], False, single) for j in range(3) if abs(values[j]) > 1e-9
        ]
        colors = [(0.3, 0.8, 1, 1), (1, 0.4, 0.8, 1), (1, 0.9, 0.3, 1), (0.5, 1, 0.5, 1)]

        mode = props.force_display
        if mode in ("PARALLELOGRAM", "TIP_TO_TAIL"):
            # A single force has nothing to add to, so show it resolved into its components instead:
            # they are the legs of its parallelogram, and it is the diagonal.
            vectors = (
                components
                if len(forces) == 1
                else [(f, colors[i % len(colors)], True, activities[i]) for i, f in enumerate(forces)]
            )
            show_resultant = len(vectors) > 1
        elif mode == "RESULTANT":
            vectors, show_resultant = [], True
        else:
            vectors = components
            # A resultant drawn over a single component would only hide it.
            show_resultant = mode == "BOTH" and len(components) > 1

        start = location
        running = np.zeros(3)
        arcs_at_tail: dict[tuple, int] = {}
        reference_axes: dict[tuple, tuple] = {}
        # Labels go at the tips. In a tip-to-tail chain, where every tip is the next tail, they lean outside the
        # polygon the chain and its resultant make, and keep off the next arrow as labels keep off lines.
        chain = np.cumsum([np.zeros(3)] + [vector for vector, *_ in vectors], axis=0) * scale + location
        centre = chain.mean(axis=0) if mode == "TIP_TO_TAIL" else None
        # A push arrives at its point. Drawn alone, its picture is mirrored through the point, arrows
        # reversed; added to others, it is slid along its line to pull, by the principle of transmissibility.
        ifc_file = tool.Ifc.get()
        pushes = {a for a in activities if a and tool.Structural.get_push(ifc_file.by_id(a))}
        arriving = len(activities) == 1 and activities[0] in pushes
        flip = lambda point: 2 * location - point if arriving else point
        for i, (vector, color, has_angle, activity) in enumerate(vectors):
            tail = start if mode == "TIP_TO_TAIL" else location
            if mode == "PARALLELOGRAM" and i:
                # Complete the parallelogram of the vectors so far and this one. Each side is coloured
                # as the vector it is parallel to; the sum of the vectors so far is a resultant, in white.
                corner = location + (running + vector) * scale
                running_color = vectors[0][1] if i == 1 else (1, 1, 1, 1)
                self.add_dashed_line(flip(location + running * scale), flip(corner), size, color)
                self.add_dashed_line(flip(location + vector * scale), flip(corner), size, running_color)
                if i < len(vectors) - 1:
                    self.add_dashed_line(location, flip(corner), size, (1, 1, 1, 1))  # An intermediate resultant.
            tip = tail + vector * scale
            label = f"{np.linalg.norm(vector):.{props.force_decimals}f} {self.force_unit}"
            if has_angle:
                label += self.get_unknown_marks(activity)[0]
            force_of = activity if has_angle else 0
            side = None  # Beside a tip-to-tail chain's polygon, if it is one.
            if has_angle and activity in pushes:
                # Slid along its line to pull, with the line it arrives along shown beyond the point.
                label += " (push)"
                self.add_dashed_line(location, location - vector * scale * 0.4, size, color)
            if arriving:
                side = None
                picked = self.add_force_arrow(
                    flip(tip), flip(tail), color, label, size, activity=activity, force_of=force_of, label_at_tail=True
                )
            elif centre is None:
                picked = self.add_force_arrow(tail, tip, color, label, size, activity=activity, force_of=force_of)
            else:
                side = self.get_label_side(vector, (tail + tip) / 2 - centre)
                onward = vector / np.linalg.norm(vector) + side  # Past the tip, leaning outside the polygon.
                picked = self.add_force_arrow(
                    tail,
                    tip,
                    color,
                    label,
                    size,
                    label_away=onward / np.linalg.norm(onward),
                    activity=activity,
                    force_of=force_of,
                )
            if not has_angle:
                # A component, tagged with its axis so that a report can name it, as F_x1 or R_x.
                k = int(np.argmax(np.abs(axes.T @ vector)))
                tilted = props.reference_frame == "LOCAL_COORDS" and not np.allclose(rotation, np.eye(3))
                self.text_info[-1]["component"] = "xyz"[k] + ("′" if tilted else "")
                if not tilted and picked is not None:
                    # Clicked, its arrow or its value, its own component is ready to type; Edit Load takes X, Y and
                    # Z, not x' and z'.
                    self.text_info[-1]["focus"] = self.pickables[picked]["focus"] = "xyz"[k]
            if props.show_force_angles and has_angle:
                self.add_force_angle(tail, vector, size, color, arcs_at_tail, reference_axes, activity, pickable=picked)
            if props.show_force_slopes and has_angle:
                arrow = (flip(tip), flip(tail)) if arriving else (tail, tip)
                avoid = None if centre is None else side
                self.add_force_slope(*arrow, size, color, activity, avoid=avoid, pickable=picked)
            start = tip
            running = running + vector

        if show_resultant and not in_equilibrium:
            label = f"{'R = ' if len(forces) > 1 else ''}{np.linalg.norm(resultant):.{props.force_decimals}f} {self.force_unit}"
            label += resultant_marks[0]
            if abs(resultant[1]) < 1e-9 and not props.show_force_angles:
                label += f" at {np.degrees(np.arctan2(resultant[2], resultant[0])):.{props.angle_decimals}f} deg"
                label += resultant_marks[1]
            # Alpha 2 because the shader caps opacity at half of it; the resultant draws fully opaque.
            # Labelled to the side, as a resultant often runs along one of the forces: outside the chain's
            # polygon, or else above.
            tip = location + resultant * scale
            outside = np.array((0, 0, 1.0)) if centre is None else (location + tip) / 2 - centre
            side = self.get_label_side(resultant, outside)
            picked = self.add_force_arrow(
                flip(tip) if arriving else location,
                location if arriving else tip,
                (1, 1, 1, 2),
                label,
                size,
                spacing=0.3,
                label_away=None if arriving else side,
                activity=single,
                resultant_of=activities if len(activities) > 1 else None,
                force_of=single,
                label_at_tail=arriving,
            )
            if props.show_force_angles:
                # In global terms, so only while the frame shown is global.
                local = props.reference_frame == "LOCAL_COORDS" and not np.allclose(rotation, np.eye(3))
                self.add_force_angle(
                    location,
                    resultant,
                    size,
                    (1, 1, 1, 1),
                    arcs_at_tail,
                    reference_axes,
                    single or None,
                    measured_from=None if local else self.get_resultant_eighth(activities),
                    pickable=picked,
                    marks=resultant_marks,
                )
            if props.show_force_slopes:
                arrow = (flip(tip), location) if arriving else (location, tip)
                self.add_force_slope(*arrow, size, (1, 1, 1, 1), avoid=side, pickable=picked, marks=resultant_marks)
        if show_resultant and in_equilibrium and len(forces) > 1:
            self.add_equilibrium_marker(location, size, activities)
        self.add_reference_axes(reference_axes, size)
        point = self.get_activities_item(activities)
        self.add_global_axes(location, size, first, point.id() if point else 0, activities)
        if not np.allclose(rotation, np.eye(3)):
            drawn = [vector * scale for vector, *_ in vectors] + ([resultant * scale] if show_resultant else [])
            self.add_point_axes(location, rotation, size, slope, drawn, point.id() if point else 0)
        self.add_symbols(self.text_info[first_text:], numbers)

    def draw_resolved_point_forces(
        self,
        object_name: str,
        forces: list[np.ndarray],
        rotation: np.ndarray,
        colors: list[tuple],
        activities: list[int],
        slope: Union[tuple[float, float], None] = None,
    ) -> None:
        """Draw each force at a point resolved along the point's own axes, as a report shows them along an incline.

        Each force is drawn as its components' resultant is, its components along x' and z' in their axes'
        colours, and the sides of its rectangle dashed, whatever the forces are shown as in the viewport.

        :param forces: The X, Y and Z components of each force, in global coordinates.
        :param colors: The colour each force is drawn in.
        :param slope: The rise and run the axes were set by, if they were.
        """
        props = tool.Structural.get_structural_props()
        location = np.zeros(3)  # A report's diagram is drawn on its own, so wherever the point is.
        longest = max((np.linalg.norm(force) for force in forces), default=0.0)
        if not longest:
            return
        scale, size = 2 / longest, 2.0
        start = len(self.info), len(self.text_info)
        drawn = []
        pushes = {a for a in activities if a and tool.Structural.get_push(tool.Ifc.get().by_id(a))}
        axes = ((0, "x′", (1, 0, 0, 1)), (2, "z′", (0, 0, 1, 1)))
        for force, color, activity in zip(forces, colors, activities):
            tip = location + force * scale
            for k, name, axis_color in axes:
                value = float(rotation[:, k] @ force)
                if abs(value) < 1e-9 * longest:
                    continue
                corner = location + rotation[:, k] * value * scale
                # The side across from a component is parallel to the other axis, so takes its colour.
                other = next(c for j, _, c in axes if j != k)
                self.add_dashed_line(corner, tip, size, other)
                label = f"{abs(value):.{props.force_decimals}f} {self.force_unit}"
                self.add_force_arrow(location, corner, axis_color, label, size)
                self.text_info[-1] |= {"component": name, "component_of": activity}
                drawn.append(corner - location)
            label = f"{np.linalg.norm(force):.{props.force_decimals}f} {self.force_unit}"
            label += self.get_unknown_marks(activity)[0] + (" (push)" if activity in pushes else "")
            self.add_force_arrow(location, tip, color, label, size, spacing=0.3, force_of=activity)
            drawn.append(tip - location)
        self.add_global_axes(location, size, start[0])
        self.add_point_axes(location, rotation, size, slope, drawn)
        self.add_symbols(self.text_info[start[1] :], {a: i for i, a in enumerate(activities, 1) if a})
        for entry in self.info[start[0] :] + self.text_info[start[1] :]:
            entry["object"] = object_name

    def add_equilibrium_marker(self, location: np.ndarray, size: float, activities: list[int]) -> None:
        """Label forces in equilibrium at a point R = 0, in place of the resultant, a label that can be clicked to
        edit the resultant as its value would be"""
        self.pickables.append(
            {
                "tail": location,
                "tip": location,
                "activity": 0,
                "info": None,
                "activities": activities,
                "label_only": True,
            }
        )
        away = np.array((1.0, 0, 0.4)) / np.linalg.norm((1.0, 0, 0.4))
        text = {"position": location, "text": f"R = 0 {self.force_unit}", "color": (1, 1, 1, 1), "away": away}
        self.text_info.append(text | {"pickable": len(self.pickables) - 1, "part": "magnitude"})

    def add_symbols(self, texts: list[dict], numbers: dict[int, int]) -> None:
        """Name each force's and component's label by its symbol in the calculations, as F_{1}: a force by its
        number, a single force's components as its own, F_{x1}, several forces' as their resultant's, R_{x}, and
        a force's components resolved apart as its own"""
        for text in texts:
            if text.get("force_of") in numbers:
                text["symbol"] = f"F_{{{numbers[text['force_of']]}}}"
            elif (axis := text.get("component")) and text.get("component_of") in numbers:
                text["symbol"] = f"F_{{{axis}{numbers[text['component_of']]}}}"
            elif axis and len(numbers) == 1:
                text["symbol"] = f"F_{{{axis}{next(iter(numbers.values()))}}}"
            elif axis and numbers:
                text["symbol"] = f"R_{{{axis}}}"

    def add_global_axes(
        self,
        location: np.ndarray,
        size: float,
        first: int = 0,
        item: int = 0,
        activities: Union[list[int], None] = None,
    ) -> None:
        """Mark the global X and Z axes through a point, faint and dashed, named at their positive ends, so that a
        diagram reads on its own, as a report's does. Y runs into the view.

        :param first: Where the point's drawing starts in the drawing data: each way, an axis reaches just past
            what is drawn there, or a short way if nothing is.
        :param item: The point's id, to make the axes' names a pickable that adds a load there, beside the
            applied loads given, as Add Load does.
        """
        first_axis, first_text = len(self.info), len(self.text_info)
        ends = [
            np.array(p) - location
            for entry in self.info[first:]
            if (primitive := entry.get("primitive"))
            for k in ("tail", "tip", "start", "end")
            if (p := primitive.get(k)) is not None
        ]
        color, past = (0.55, 0.55, 0.55, 1), size * 0.1
        reaches = {}
        for k, name in ((0, "+X"), (2, "+Z")):
            axis = np.eye(3)[k]
            low = min([0.0] + [p[k] for p in ends]) - past
            high = max([0.0] + [p[k] for p in ends]) + past
            reaches[k] = (low, high)
            self.add_dashed_line(location + axis * low, location + axis * high, size, color)
            self.text_info.append({"position": location + axis * high, "text": name, "color": color, "away": axis})
        # Y as far as the longer of them reaches, as forces in the X-Z plane give it no length of its own. Seen
        # orbiting the view; a report, looking along Y, leaves it out.
        reach = max(max(abs(low), abs(high)) for low, high in reaches.values())
        axis = np.array((0, 1.0, 0))
        self.add_dashed_line(location - axis * reach, location + axis * reach, size, color)
        self.info[-1]["along_view"] = True
        text = {"position": location + axis * reach, "text": "+Y", "color": color, "away": axis, "along_view": True}
        self.text_info.append(text)
        if item and activities:
            self.pickables.append(
                {
                    "tail": location,
                    "tip": location,
                    "activity": 0,
                    "info": first_axis,
                    "add_load_to": item,
                    "with_activities": activities,
                    "label_only": True,
                }
            )
            self.join_pickable(len(self.pickables) - 1, first_axis, self.text_info[first_text:], "add")

    def add_point_axes(
        self,
        location: np.ndarray,
        rotation: np.ndarray,
        size: float,
        slope: Union[tuple[float, float], None] = None,
        drawn: Union[list[np.ndarray], None] = None,
        item: int = 0,
    ) -> None:
        """Mark a point's own axes, and, given the point's id, make them a pickable that edits them: clicked, a
        value, the tilt or a slope's rise or run, is ready to type over, as forces' values are"""
        first = len(self.info)
        parts = self.draw_point_axes(location, rotation, size, slope, drawn)
        if item:
            self.pickables.append(
                {"tail": location, "tip": location, "activity": 0, "info": first, "axes_of": item, "label_only": True}
            )
            ends = parts[1:] + [("", len(self.info), len(self.text_info))]
            for (part, info, text), (_, next_info, next_text) in zip(parts, ends):
                self.join_pickable(len(self.pickables) - 1, info, self.text_info[text:next_text], part, next_info)

    def draw_point_axes(
        self,
        location: np.ndarray,
        rotation: np.ndarray,
        size: float,
        slope: Union[tuple[float, float], None] = None,
        drawn: Union[list[np.ndarray], None] = None,
    ) -> list[tuple[str, int, int]]:
        """Mark a point's own axes, x' and z' coloured as their components, and their tilt if in X-Z.

        :param slope: The rise and run the axes were set by, shown as a triangle under x' beside the angle.
        :param drawn: The arrows drawn from the point, as drawn, to keep the triangle clear of.
        :return: Where each part starts in the drawing data and labels: the axes, the slope and the angle.
        """
        parts = [("axes", len(self.info), len(self.text_info))]
        x_axis = rotation[:, 0]
        # The triangle goes on the side of the point that arrows along x' reach least into.
        reach = lambda side: max(
            [side * float(v @ x_axis) for v in drawn or [] if abs(float(v @ x_axis)) > 0.7 * np.linalg.norm(v)] + [0.0]
        )
        side = 1.0 if reach(1.0) <= reach(-1.0) else -1.0
        for k, name, color in ((0, "x′", (1, 0.35, 0.35, 1)), (2, "z′", (0.4, 0.55, 1, 1))):
            axis = rotation[:, k]
            back = 0.75 if k == 0 and slope and side < 0 else 0.3  # Far enough back to carry a triangle there.
            self.add_dashed_line(location - axis * size * back, location + axis * size * 0.85, size, color)
            self.text_info.append(
                {"position": location + axis * size * 0.85, "text": name, "color": color, "away": axis}
            )
        if abs(x_axis[1]) > 1e-6:
            return parts  # Turned out of the X-Z plane, so one tilt does not describe it.
        tilt = np.degrees(np.arctan2(x_axis[2], x_axis[0]))
        if abs(tilt) < 0.01:
            return parts
        color = (1, 0.35, 0.35, 1)
        if slope and abs(x_axis[0]) > 1e-6 and abs(x_axis[2]) > 1e-6:
            parts.append(("slope", len(self.info), len(self.text_info)))
            # The incline as given: its hypotenuse along x', its legs level and plumb, the corner beneath.
            a, b = location + side * x_axis * size * 0.35, location + side * x_axis * size * 0.7
            low, high = (a, b) if a[2] < b[2] else (b, a)
            corner = np.array((high[0], high[1], low[2]))
            for start, end in ((a, corner), (corner, b), (a, b)):
                self.add_dashed_line(start, end, size, color, dashed=False)
            centroid = (a + b + corner) / 3
            for p, q in ((a, corner), (corner, b)):
                level = abs(p[2] - q[2]) < 1e-9
                middle = (p + q) / 2
                away = (middle - centroid) / np.linalg.norm(middle - centroid)
                text = f"{abs(slope[1] if level else slope[0]):g}"
                leg = "run" if level else "rise"
                self.text_info.append({"position": middle, "text": text, "color": color, "away": away, "focus": leg})
        # The tilt from +X, as an arc like the force angles, with +X marked where it starts. On the side kept
        # clear of arrows, from -X to -x', which makes the same angle with the horizontal.
        parts.append(("angle", len(self.info), len(self.text_info)))
        radius = size * 0.12
        start = 180.0 if side < 0 and abs(tilt) <= 90 else 0.0
        level = np.array((np.cos(np.radians(start)), 0, 0))
        self.add_dashed_line(location, location + level * size * 0.2, size, color)
        steps = max(4, int(abs(tilt) / 5))
        points = [
            location + radius * np.array((np.cos(a), 0, np.sin(a)))
            for a in np.radians(np.linspace(start, start + tilt, steps + 1))
        ]
        for a, b in zip(points, points[1:]):
            self.add_dashed_line(a, b, size, color, dashed=False)
        middle = np.radians(start + tilt / 2)
        outward = np.array((np.cos(middle), 0, np.sin(middle)))
        self.text_info.append(
            {
                "position": location + radius * outward,
                "text": f"{abs(tilt):.1f}°",
                "color": color,
                "away": outward,
                "focus": "angle",
            }
        )
        return parts

    def get_unknown_marks(self, activity: Union[int, None]) -> tuple[str, str]:
        """Marks for an applied load's magnitude and direction labels, if they are unknown: to be found"""
        if not activity:
            return "", ""
        element = tool.Ifc.get().by_id(activity)
        magnitude, direction = tool.Structural.get_locks(element)
        # A magnitude following from a known component is found too.
        magnitude = magnitude and not tool.Structural.get_known_component(element)
        return ("" if magnitude else " 🔓"), ("" if direction else " 🔓")

    def get_resultant_marks(self, activities: list[int]) -> tuple[str, str]:
        """Marks for a resultant's magnitude and direction labels, if they were found: a single force's own, or what
        Edit Resultant finds of the resultant of several, as the report's table marks it"""
        if len(activities) == 1:
            return self.get_unknown_marks(activities[0])
        if not activities or not all(activities):
            return "", ""
        elements = [tool.Ifc.get().by_id(a) for a in activities]
        locks = [tool.Structural.get_locks(element) for element in elements]
        found = tool.Structural.get_resultant_found(locks, tool.Structural.get_magnitude_groups(elements))
        return (" 🔓" if "magnitude" in found else ""), (" 🔓" if "direction" in found else "")

    def add_force_angle(
        self,
        tail: np.ndarray,
        vector: np.ndarray,
        size: float,
        color: tuple,
        arcs_at_tail: dict[tuple, int],
        reference_axes: dict[tuple, tuple],
        activity: Union[int, None] = None,
        measured_from: Union[str, None] = None,
        pickable: Union[int, None] = None,
        marks: Union[tuple[str, str], None] = None,
    ) -> None:
        """Mark a force's angle from a reference axis, as an arc in the X-Z plane.

        :param measured_from: An eighth chosen to measure it from, as a resultant's can be.
        :param pickable: The force's pickable, which its arc and label join, to be clicked and highlighted with it.
        :param marks: The magnitude and direction marks, as a resultant's, if not its applied load's.
        """
        if abs(vector[1]) > 1e-9 * np.linalg.norm(vector):
            return  # Not in the X-Z plane, so one angle does not describe it.
        first = len(self.info)
        props = tool.Structural.get_structural_props()
        start, end, eighth = self.get_angle_reference(vector, props.angle_reference, activity, measured_from)
        if abs(end - start) < 0.01:
            return
        key = tuple(np.round(tail, 6))
        arcs_at_tail.setdefault(key, 0)
        # Arcs sharing a tail get growing radii so that they do not overlap.
        radius = size * (0.18 + 0.05 * arcs_at_tail[key])
        arcs_at_tail[key] += 1
        reference_axes.setdefault((key, start), (tail, start, []))[2].append((radius, color))
        steps = max(4, int(abs(end - start) / 5))
        points = [
            tail + radius * np.array((np.cos(a), 0, np.sin(a))) for a in np.radians(np.linspace(start, end, steps + 1))
        ]
        for a, b in zip(points, points[1:]):
            self.add_dashed_line(a, b, size, color, dashed=False)
        middle = np.radians((start + end) / 2)
        outward = np.array((np.cos(middle), 0, np.sin(middle)))
        # Away from the arc, and off the reference axis towards the force so small angles keep off the lines.
        axis = np.array((np.cos(np.radians(start)), 0, np.sin(np.radians(start))))
        across = vector / np.linalg.norm(vector) - np.dot(vector, axis) / np.linalg.norm(vector) * axis
        away = outward + across / (np.linalg.norm(across) or 1)
        angle = end if props.angle_reference == "POSITIVE_X" else abs(end - start)
        self.text_info.append(
            {
                "position": tail + radius * outward,
                "text": f"θ = {angle:.{props.angle_decimals}f}°{f' {eighth}' if eighth else ''}"
                + (marks or self.get_unknown_marks(activity))[1],
                "color": color,
                "away": away / np.linalg.norm(away),
                "focus": "angle",
            }
        )
        self.join_pickable(pickable, first, self.text_info[-1:], "angle")

    def get_activities_item(self, activities: list[int]) -> Union[ifcopenshell.entity_instance, None]:
        """The structural item applied loads act on, by the first's id"""
        if not activities or not activities[0]:
            return None
        connects = tool.Ifc.get().by_id(activities[0]).AssignedToStructuralItem
        return connects[0].RelatingElement if connects else None

    def get_resultant_eighth(self, activities: list[int]) -> Union[str, None]:
        """The eighth chosen for the angle of the resultant of applied loads, as Edit Resultant previews or keeps it"""
        if not activities or not activities[0]:
            return None
        activity = tool.Ifc.get().by_id(activities[0])
        connects = activity.AssignedToStructuralItem
        if not connects or not (load_case := tool.Structural.get_activity_load_case(activity)):
            return None
        item = connects[0].RelatingElement
        if item.id() in self.preview_resultant_eighths:
            return self.preview_resultant_eighths[item.id()]
        return tool.Structural.get_resultant_eighth(item, load_case)

    def get_angle_reference(
        self,
        vector: np.ndarray,
        reference: str,
        activity: Union[int, None] = None,
        measured_from: Union[str, None] = None,
    ) -> tuple[float, float, Union[str, None]]:
        """Get the angles in degrees of the axis a force in the X-Z plane is measured from and of the force,
        counter-clockwise from +X, and the eighth it is measured in, if by eighths"""
        end = np.degrees(np.arctan2(vector[2], vector[0]))
        start = 0.0
        eighth = None
        chosen = tool.Structural.get_angle_from_eighth(vector[0], vector[2], measured_from) if measured_from else None
        if chosen is not None and reference != "POSITIVE_X":
            # The eighth chosen for it: from that eighth's axis, turning its way, however far.
            eighth = measured_from
            start = 90.0 * (int(eighth[1]) // 2)
            end = start + (chosen if int(eighth[1]) % 2 else -chosen)
        elif reference == "EIGHTH":
            # From the axis of the eighth Edit Load enters it in, which its generated name records: one of the
            # point's own axes if the eighth is primed, as the force was entered against them.
            load = tool.Ifc.get().by_id(activity).AppliedLoad if activity else None
            named = re.search(r" (Q[1-8])′?$", (load.Name or "") if load else "")
            tilt = self.get_entry_tilt(activity)
            x, z = tool.Structural.to_axes(vector[0], vector[2], tilt) if tilt else (vector[0], vector[2])
            eighth, angle, _, _ = tool.Structural.get_eighth(x, z, named[1] if named else None)
            start = tilt + 90.0 * (int(eighth[1]) // 2)
            end = start + (angle if int(eighth[1]) % 2 else -angle)
            eighth += "′" if tilt else ""
        elif reference == "HORIZONTAL" and vector[0] < -1e-9 * np.linalg.norm(vector):
            # Measured from -X, so that the angle is the acute one statics texts draw.
            start = 180.0
            end = end if end > 0 else end + 360
        return start, end, eighth

    def join_pickable(
        self, pickable: Union[int, None], first: int, texts: list[dict], part: str, end: Union[int, None] = None
    ) -> None:
        """Make the lines drawn from first, to end or so far, and labels, a part of a force's pickable, as its angle
        is: clicked, they edit the force, and hovered, the part is highlighted on its own"""
        if pickable is None:
            return
        parts = self.pickables[pickable].setdefault("parts", {})
        parts.setdefault(part, []).extend(range(first, len(self.info) if end is None else end))
        for text in texts:
            text["pickable"], text["part"] = pickable, part

    def get_entry_tilt(self, activity: Union[int, None]) -> float:
        """The tilt of the point's own axes an applied load was entered against, as a primed eighth in its
        generated name records, or 0 if it was entered against X and Z, or the frame shown is not global"""
        if not activity or tool.Structural.get_structural_props().reference_frame == "LOCAL_COORDS":
            return 0.0
        element = tool.Ifc.get().by_id(activity)
        if not element.AppliedLoad or not re.search(r" Q[1-8]′$", element.AppliedLoad.Name or ""):
            return 0.0
        connects = element.AssignedToStructuralItem
        return (tool.Structural.get_axes_tilt(connects[0].RelatingElement) if connects else None) or 0.0

    def add_force_slope(
        self,
        tail: np.ndarray,
        tip: np.ndarray,
        size: float,
        color: tuple,
        activity: Union[int, None] = None,
        avoid: Union[np.ndarray, None] = None,
        pickable: Union[int, None] = None,
        marks: Union[tuple[str, str], None] = None,
    ) -> None:
        """Mark a force's slope as a triangle beside it, its legs along and across the axis its angle is from.

        :param avoid: The side of the force its label is on, to keep the triangle off it.
        :param pickable: The force's pickable, which its triangle and labels join, as its angle's do.
        :param marks: The magnitude and direction marks, as a resultant's, if not its applied load's.
        """
        first, first_text = len(self.info), len(self.text_info)
        vector = tip - tail
        length = np.linalg.norm(vector)
        if not length or abs(vector[1]) > 1e-9 * length:
            return  # Not in the X-Z plane, so one slope does not describe it.
        props = tool.Structural.get_structural_props()
        # A full turn from +X makes no triangle, so measure from the nearest horizontal instead.
        reference = "HORIZONTAL" if props.angle_reference == "POSITIVE_X" else props.angle_reference
        start, end, _ = self.get_angle_reference(vector, reference, activity)
        turned = np.radians(end - start)
        along, across = abs(np.cos(turned)), abs(np.sin(turned))
        if along < 1e-6 or across < 1e-6:
            return  # Along or square to the axis, so there is no slope to show.
        direction = vector / length
        # The run lies along X and the rise along Z, or along x' and z' for a force entered against the point's
        # own axes, as its angle is measured from them.
        tilt = np.radians(self.get_entry_tilt(activity) if reference == "EIGHTH" else 0.0)
        run_axis, rise_axis = np.array((np.cos(tilt), 0, np.sin(tilt))), np.array((-np.sin(tilt), 0, np.cos(tilt)))
        level, plumb = abs(float(direction @ run_axis)), abs(float(direction @ rise_axis))
        # Rise over run, as a roof pitch is given: whole numbers when small ones fit, else the rise to a run of 1.
        rise, run = tool.Structural.get_simple_slope(level, plumb)
        if float(rise).is_integer() and float(run).is_integer():
            rise_text, run_text = f"{abs(rise):g}", f"{abs(run):g}"
        else:
            rise_text, run_text = f"{plumb / level:.3g}", "1"
        axis = np.array((np.cos(np.radians(start)), 0, np.sin(np.radians(start))))
        # The run is the same length on every triangle, so that they compare, the rise showing the
        # slope; a steep force keeps its rise to 2.5 runs, shortening its run instead. The hypotenuse lies along
        # the force, out towards its tip, beyond the angle arcs at its tail and short of its head, and the legs meet
        # off to one side; on a short force it moves back to fit, and only a force too short to hold it shrinks it.
        run_length = size * 0.1125
        hypotenuse = min(run_length / level if level else np.inf, 2.5 * run_length / plumb if plumb else np.inf)
        end = length - size * 0.06  # Short of the head.
        near = min(max(length * 0.75 - hypotenuse / 2, size * 0.3), end - hypotenuse)
        if near < size * 0.05:
            near, hypotenuse = size * 0.05, max(end - size * 0.05, 0.0)
        if hypotenuse * min(along, across) < run_length * 0.15:
            return  # A sliver too flat to read, as for a force nearly along the axis; its angle says it.

        def build(near: float, away_from_axis: bool) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
            """The triangle's corners: the hypotenuse's ends along the force, and where the legs meet"""
            a = tail + direction * near
            b = a + direction * hypotenuse
            # Turned to the other side, the same triangle meets at the hypotenuse's far end.
            corner = (
                b - axis * hypotenuse * np.cos(turned) if away_from_axis else a + axis * hypotenuse * np.cos(turned)
            )
            side = corner - a - np.dot(corner - a, direction) * direction
            offset = side / np.linalg.norm(side) * size * 0.05
            return a + offset, b + offset, corner + offset

        # The angle's arc and label lie between the force and its axis, so the triangle goes on the other side.
        away_from_axis = bool(props.show_force_angles)
        a, b, corner = build(near, away_from_axis)
        if avoid is not None and np.dot(corner - a, avoid) > 0:
            away_from_axis = not away_from_axis
        # Off lines drawn at the point already, as another force's triangle along a force beside it: further back
        # along the force first, then on the other side, the first place clear.
        drawn = self.get_point_segments(tail, tip)
        flat = lambda p: (p[0], p[2])
        crosses = lambda corners: any(
            segments_cross(flat(p), flat(q), s, e)
            for p, q in ((corners[0], corners[2]), (corners[2], corners[1]), (corners[0], corners[1]))
            for s, e in drawn
        )
        places = [n for n in (near, near - hypotenuse * 0.6, near - hypotenuse * 1.2) if n >= size * 0.05]
        a, b, corner = next(
            (c for side in (away_from_axis, not away_from_axis) for n in places if not crosses(c := build(n, side))),
            build(near, away_from_axis),
        )
        for start_point, end_point in ((a, corner), (corner, b), (a, b)):
            self.add_dashed_line(start_point, end_point, size, color, dashed=False)
        centroid = (a + b + corner) / 3
        for p, q in ((a, corner), (corner, b)):
            # The leg along the run's axis is the run, and the other the rise.
            leg = "run" if abs(float((q - p) @ run_axis)) > abs(float((q - p) @ rise_axis)) else "rise"
            middle = (p + q) / 2
            away = middle - centroid
            self.text_info.append(
                {
                    "position": middle,
                    # An unknown direction marked once, on the rise.
                    "text": run_text if leg == "run" else rise_text + (marks or self.get_unknown_marks(activity))[1],
                    "color": color,
                    "away": away / np.linalg.norm(away),
                    "focus": leg,
                }
            )
        self.join_pickable(pickable, first, self.text_info[first_text:], "slope")

    def get_point_segments(self, tail: np.ndarray, tip: np.ndarray) -> list[tuple[tuple, tuple]]:
        """The arrows and solid lines drawn at the point so far, in the X-Z plane, but a force's own arrow, from
        tail to tip, which its slope triangle lies beside"""
        flat = lambda p: (float(p[0]), float(p[2]))
        own = {flat(tail), flat(tip)}
        segments = []
        for entry in self.info[getattr(self, "point_first", 0) :]:
            if not (primitive := entry.get("primitive")):
                continue
            if primitive["type"] == "ARROW":
                ends = (flat(primitive["tail"]), flat(primitive["tip"]))
                if set(ends) == own:
                    continue
            elif not primitive["dashed"]:
                ends = (flat(primitive["start"]), flat(primitive["end"]))
            else:
                continue  # Dashed guides may be crossed.
            segments.append(ends)
        return segments

    def add_reference_axes(self, reference_axes: dict[tuple, tuple], size: float) -> None:
        """Draw the axes angles are measured from, each band coloured as the arc that starts in it"""
        for tail, start, arcs in reference_axes.values():
            direction = np.array((np.cos(np.radians(start)), 0, np.sin(np.radians(start))))
            arcs.sort(key=lambda arc: arc[0])
            band_start = 0.0
            for i, (radius, color) in enumerate(arcs):
                # Bands end just past their arc, before the next arc out; the last runs on to the axis' length.
                band_end = radius + size * 0.04 if i < len(arcs) - 1 else max(radius + size * 0.04, size * 0.45)
                self.add_dashed_line(tail + direction * band_start, tail + direction * band_end, size, color)
                band_start = band_end

    def get_label_side(self, vector: np.ndarray, towards: np.ndarray) -> np.ndarray:
        """Get the direction square to a vector, in the X-Z plane where possible, on the side of towards"""
        direction = vector / np.linalg.norm(vector)
        side = np.array((-direction[2], 0, direction[0]))
        if not np.linalg.norm(side):
            side = self.get_perpendicular_axes(direction)[0]
        if np.dot(side, towards) < 0 or (abs(np.dot(side, towards)) < 1e-9 and side[2] < 0):
            side = -side
        return side / np.linalg.norm(side)

    def get_perpendicular_axes(self, direction: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        helper = np.array((0, 0, 1)) if abs(direction[2]) < 0.9 else np.array((1, 0, 0))
        d2 = np.cross(direction, helper)
        d2 = d2 / np.linalg.norm(d2)
        return d2, np.cross(direction, d2)

    def add_force_arrow(
        self,
        tail: np.ndarray,
        tip: np.ndarray,
        color: tuple,
        label: str,
        size: float,
        spacing: float = 0.2,
        label_away: Union[np.ndarray, None] = None,
        activity: int = 0,
        resultant_of: Union[list[int], None] = None,
        force_of: int = 0,
        label_at_tail: bool = False,
    ) -> Union[int, None]:
        """Add an arrow from tail to tip, its head and shaft sized to size, the longest arrow drawn with it.

        :param force_of: The activity whose whole force the arrow is, not a component, to name it in a report.
        :param label_at_tail: Label it beyond its tail, as a push arriving at its point is.
        """
        length = np.linalg.norm(tip - tail)
        if not length:
            return
        direction = (tip - tail) / length
        # The shader works in units of a fifth of size: the head is 2 * spacing of them long.
        unit = size / 5
        d2, d3 = self.get_perpendicular_axes(direction)
        d2, d3 = d2 * unit, d3 * unit
        self.info.append(
            {
                "shader": self.shader.new("SINGLE FORCE"),
                "args": {
                    "position": [tip, tail + d2, tail - d2, tail + d3, tail - d3],
                    "coord": [
                        (0, 0, 0),
                        (1, length / unit, 0),
                        (-1, length / unit, 0),
                        (1, length / unit, 0),
                        (-1, length / unit, 0),
                    ],
                },
                "indices": [(0, 1, 2), (0, 3, 4)],
                "uniforms": [["color", color], ["spacing", spacing]],
                # The arrow itself, for drawing it elsewhere than the viewport, as in a report.
                "primitive": {"type": "ARROW", "tail": tail, "tip": tip, "size": size, "spacing": spacing},
                "color": color,
            }
        )
        picked = None
        if activity or resultant_of:
            pickable = {"tail": tail, "tip": tip, "activity": activity, "info": len(self.info) - 1}
            if resultant_of:
                pickable["activities"] = resultant_of
            self.pickables.append(pickable)
            picked = len(self.pickables) - 1
        # Labelled beside the tip, as arrows often share their tail.
        away = (-direction if label_at_tail else direction) if label_away is None else label_away
        position = tail if label_at_tail else tip
        text = {"position": position, "text": label, "color": color, "away": away}
        if picked is not None:
            text["pickable"] = picked  # Its value can be clicked as the arrow can, to type over its magnitude.
            text["focus"], text["part"] = "magnitude", "magnitude"
        if force_of:
            text["force_of"] = force_of
        self.text_info.append(text)
        return picked

    def add_dashed_line(
        self, start: np.ndarray, end: np.ndarray, size: float, color: tuple, dashed: bool = True
    ) -> None:
        width = size * 0.003
        length = np.linalg.norm(end - start)
        if not length:
            return
        d2, d3 = self.get_perpendicular_axes((end - start) / length)
        position, indices = [], []
        for axis in (d2, d3):
            n = len(position)
            position += [start + width * axis, start - width * axis, end + width * axis, end - width * axis]
            indices += [(n, n + 1, n + 2), (n + 1, n + 3, n + 2)]
        self.info.append(
            {
                "shader": self.shader.new("DASHED LINE"),
                "args": {"position": position, "coord": [(1, 0, 0), (-1, 0, 0), (1, length, 0), (-1, length, 0)] * 2},
                "indices": indices,
                # A spacing far longer than the line draws it solid.
                "uniforms": [["color", color], ["spacing", size * 0.03 if dashed else size * 1000]],
                "primitive": {"type": "LINE", "start": start, "end": end, "size": size, "dashed": dashed},
                "color": color,
            }
        )

    def get_point_moment_args(self, moments: Iterable, location: np.ndarray, rotation: np.ndarray) -> None:
        """get the args to the point shader for the X, Y and Z moments at a point"""
        location = np.array(location)
        directions: list[tuple[npt.NDArray, npt.NDArray]] = [
            (np.array((0, 1, 0)), np.array((0, 0, 1))),
            (np.array((1, 0, 0)), np.array((0, 0, 1))),
            (np.array((1, 0, 0)), np.array((0, 1, 0))),
        ]
        if tool.Structural.get_structural_props().reference_frame == "LOCAL_COORDS":
            directions = [(rotation @ a, rotation @ b) for a, b in directions]
        colors = [(1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1)]

        for moment, (direction, d2), color in zip(moments, directions, colors):
            if moment == 0:
                continue
            d1 = -(direction * moment)
            d1 = d1 / np.linalg.norm(d1)
            self.info.append(
                {
                    "shader": self.shader.new("SINGLE MOMENT"),
                    "args": {
                        "position": [location - d2, location + d1 + d2, location - d1 + d2],
                        "coord": [(-1, 0, 0), (1, 1, 0), (1, -1, 0)],
                    },
                    "indices": [(0, 1, 2)],
                    "uniforms": [["color", color]],
                }
            )
            decimals = tool.Structural.get_structural_props().force_decimals
            self.text_info.append(
                {
                    "position": location + 0.25 * (d1 + d2),
                    "text": f"{moment:.{decimals}f} {self.moment_unit}",
                    "color": color,
                }
            )

    def get_point_loads_values(
        self, activity_list: list[tuple[ifcopenshell.entity_instance, float]], element_rotation_matrix: np.ndarray
    ) -> np.ndarray:
        """returns a numpy array with the sum of the point load values"""
        result_list = np.zeros(6)
        attr_list = ["ForceX", "ForceY", "ForceZ", "MomentX", "MomentY", "MomentZ"]
        for item in activity_list:
            activity = item[0]
            factor = item[1]
            load = activity.AppliedLoad
            preview = self.preview.get(load.id()) if load else None
            temp = np.zeros(6)
            for i, attr in enumerate(attr_list):
                value = preview.get(attr) if preview is not None else getattr(load, attr, 0)
                temp[i] += (value or 0) * factor
            transform_3 = self.get_activity_transform_matrix(activity, element_rotation_matrix)
            transform_6 = np.zeros((6, 6))
            transform_6[0:3, 0:3] = transform_3
            transform_6[3:6, 3:6] = transform_3
            result_list += transform_6 @ temp

        return result_list

    def get_linear_loads(self) -> None:
        position = []
        indices = []
        sin_quad_lin = []
        coords_for_shader = []
        color = []
        info = []
        maxforce = 0

        list_of_curve_members = self.curve_members
        for value in list_of_curve_members.values():
            member = value["member"]
            self.tag_new_entries(tool.Ifc.get_object(member))
            activity_list = value["activities"]
            if len(activity_list) == 0:
                continue

            blender_object = tool.Ifc.get_object_by_identifier(getattr(member, "GlobalId", None))

            start_co = blender_object.matrix_world @ blender_object.data.vertices[0].co
            end_co = blender_object.matrix_world @ blender_object.data.vertices[1].co
            x_axis = Vector(end_co - start_co).normalized()
            z_direction = getattr(member, "Axis")
            # local coordinates
            z_axis = Vector(getattr(z_direction, "DirectionRatios", None)).normalized()
            y_axis = z_axis.cross(x_axis).normalized()
            z_axis = x_axis.cross(y_axis).normalized()
            rotation = self.get_curve_member_rotation(member)

            props = tool.Structural.get_structural_props()
            reference_frame = props.reference_frame
            is_local = reference_frame == "LOCAL_COORDS"
            x_match = abs(Vector((1, 0, 0)).dot(x_axis)) > 0.99
            y_match = abs(Vector((0, 1, 0)).dot(x_axis)) > 0.99
            z_match = abs(Vector((0, 0, 1)).dot(x_axis)) > 0.99
            direction_dict = {
                "fx": y_axis + z_axis if is_local else Vector((1, 0, 0)) if not x_match else Vector((0, 1, 1)),
                "fy": y_axis if is_local else Vector((0, 1, 0)) if not y_match else Vector((1, 0, 1)),
                "fz": z_axis if is_local else Vector((0, 0, 1)) if not z_match else Vector((1, 1, 0)),
                "mx": z_axis - y_axis if is_local or x_match else Vector((1, 0, 0)).cross(x_axis),
                "my": (
                    z_axis
                    if is_local
                    else Vector((-1, 0, 1))
                    if y_match
                    else Vector((0, 1, 0)).cross(x_axis).normalized()
                ),
                "mz": (
                    y_axis
                    if is_local
                    else Vector((-1, 1, 0))
                    if z_match
                    else Vector((0, 0, 1)).cross(x_axis).normalized()
                ),
            }
            match_dict = {"fx": x_match or is_local, "fy": y_match, "fz": z_match}
            member_length = Vector(end_co - start_co).length
            processed_loads = self.process_total_linear_loads(activity_list, rotation, member_length)
            linear_loads = processed_loads["linear loads"]
            maxforce = max(maxforce, processed_loads["max linear load"])
            point_loads = processed_loads["discrete loads"]

            if len(point_loads) > 0:
                for item in point_loads:
                    for sub_item in item:
                        pos = sub_item["pos"]
                        values = sub_item["values"]
                        pos_vector = start_co + x_axis * pos
                        self.draw_point_forces([np.array(values[:3])], pos_vector, rotation)
                        self.get_point_moment_args(values[3:], pos_vector, rotation)
            if linear_loads is None:
                continue
            keys = ["fx", "fy", "fz", "mx", "my", "mz"]

            for key in keys:
                polyline = linear_loads[key]["polyline"]
                sinus = linear_loads[key]["sinus"]
                quadratic = linear_loads[key]["quadratic"]
                constant = linear_loads[key]["constant"]
                direction = direction_dict[key]
                color_axis = (0, 0, 1, 1)
                if "x" in key:
                    color_axis = (1, 0, 0, 1)
                if "y" in key:
                    color_axis = (0, 1, 0, 1)

                if "f" in key:
                    unit = self.linear_force_unit
                    if match_dict[key]:
                        shader = self.shader.new("PARALLEL DISTRIBUTED FORCE")
                    else:
                        shader = self.shader.new("PERPENDICULAR DISTRIBUTED FORCE")
                else:
                    unit = self.linear_moment_unit
                    shader = self.shader.new("DISTRIBUTED MOMENT")

                counter = 0
                for i in range(len(polyline) - 1):
                    current = Vector(polyline[i] + [0])
                    nextitem = Vector(polyline[i + 1] + [0])

                    if any([current.y, nextitem.y, constant, quadratic, sinus]):
                        negative = -1 * direction + start_co + x_axis * current.x
                        positive = direction + start_co + x_axis * current.x
                        position.append(negative)
                        coords_for_shader.append((current.x, 1.0, member_length))
                        sin_quad_lin.append((sinus, quadratic, current.y + constant))
                        color.append(color_axis)

                        x = current.x / member_length
                        func = sin(x * 3.1416) * sinus + (-4.0 * x * x + 4.0 * x) * quadratic + constant + current.y
                        if func:
                            self.text_info.append(
                                {
                                    "position": -1 * direction * func / maxforce + start_co + x_axis * current.x,
                                    "text": f"{func:.{props.force_decimals}f} {unit}",
                                }
                            )

                        position.append(positive)
                        coords_for_shader.append((current[0], -1.0, member_length))
                        sin_quad_lin.append((sinus, quadratic, current.y + constant))
                        color.append(color_axis)

                        indices.append((0 + counter, 1 + counter, 2 + counter))
                        indices.append((3 + counter, 2 + counter, 1 + counter))
                        if i == len(polyline) - 2:
                            negative = -1 * direction + start_co + x_axis * nextitem.x
                            positive = direction + start_co + x_axis * nextitem.x
                            position.append(negative)
                            coords_for_shader.append((nextitem.x, 1.0, member_length))
                            sin_quad_lin.append((sinus, quadratic, nextitem.y + constant))
                            color.append(color_axis)

                            x = nextitem.x / member_length
                            func = (
                                sin(x * 3.1416) * sinus + (-4.0 * x * x + 4.0 * x) * quadratic + constant + nextitem.y
                            )
                            if func:
                                self.text_info.append(
                                    {
                                        "position": -1 * direction * func / maxforce + start_co + x_axis * nextitem.x,
                                        "text": f"{func:.{props.force_decimals}f} {unit}",
                                    }
                                )

                            position.append(positive)
                            coords_for_shader.append((nextitem.x, -1.0, member_length))
                            sin_quad_lin.append((sinus, quadratic, nextitem.y + constant))
                            color.append(color_axis)

                        counter += 2
                if position:
                    self.info.append(
                        {
                            "shader": shader,
                            "args": {
                                "position": position,
                                "sin_quad_lin_forces": sin_quad_lin,
                                "coord": coords_for_shader,
                            },
                            "indices": indices,
                            "uniforms": [["color", color_axis], ["spacing", 0.2], ["maxload", maxforce]],
                        }
                    )
                position = []
                sin_quad_lin = []
                coords_for_shader = []
                indices = []
            for info in self.info:
                info["uniforms"][2][1] = maxforce

    def process_total_linear_loads(
        self,
        activity_list: list[tuple[ifcopenshell.entity_instance, float]],
        element_rotation_matrix: np.ndarray,
        member_length: float,
    ) -> ProcessedLoad:
        """returns a dict with total values for applied loads in each direction
        along with the maximum value for the loads in the member and the discrete loads applied

        """
        loads_dict = self.parse_linear_loads_to_dict(activity_list, element_rotation_matrix)
        const = loads_dict["constant force"]
        quad = loads_dict["quadratic force"]
        sinus = loads_dict["sinus force"]
        loads = loads_dict["linear load configuration"]
        unique_list = self.getuniquepositionlist(loads)
        final_list = []
        distributed_loads = None
        max_load = 0
        for pos in unique_list:
            value = self.get_before_and_after(pos, loads)
            if value["before"] == value["after"]:
                final_list.append([pos] + value["before"])
            else:
                final_list.append([pos] + value["before"])
                final_list.append([pos] + value["after"])

        if len(final_list) == 0 and any(const + quad + sinus):
            final_list.append([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
            final_list.append([member_length, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])

        elif len(final_list) > 0:
            if final_list[0][0] and any(
                const + quad + sinus
            ):  # if first item location is not 0 append an item at the zero
                final_list = [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]] + final_list
            else:
                del final_list[0]
            if abs(final_list[-1][0] - member_length) > 0.01 and any(const + quad + sinus):
                final_list.append([member_length, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
            else:
                del final_list[-1]
        if len(final_list) > 0:
            array = np.array(final_list)  # 7xn -> ["pos","fx","fy","fz","mx","my","mz"]
            keys = ["fx", "fy", "fz", "mx", "my", "mz"]
            polyline = []
            distributed_loads = {
                "fx": {"constant": 0, "quadratic": 0, "sinus": 0, "polyline": []},
                "fy": {"constant": 0, "quadratic": 0, "sinus": 0, "polyline": []},
                "fz": {"constant": 0, "quadratic": 0, "sinus": 0, "polyline": []},
                "mx": {"constant": 0, "quadratic": 0, "sinus": 0, "polyline": []},
                "my": {"constant": 0, "quadratic": 0, "sinus": 0, "polyline": []},
                "mz": {"constant": 0, "quadratic": 0, "sinus": 0, "polyline": []},
            }
            max_load = 0
            for component, key in enumerate(keys):
                if any([sinus[component], quad[component], const[component]]) or any(
                    item for item in array[:, component + 1]
                ):
                    for currentitem in final_list:
                        polyline.append([currentitem[0], currentitem[component + 1]])
                        max_load = max(
                            max_load,
                            abs(sinus[component] + quad[component] + const[component] + currentitem[component + 1]),
                        )
                    inner_dict = distributed_loads[key]
                    inner_dict["constant"] = const[component]
                    inner_dict["quadratic"] = quad[component]
                    inner_dict["sinus"] = sinus[component]
                    inner_dict["polyline"] = polyline
                    distributed_loads[key] = inner_dict

        return {
            "linear loads": distributed_loads,
            "max linear load": max_load,
            "discrete loads": loads_dict["point load configuration"],
        }

    def getuniquepositionlist(self, load_config_list: list[list[LoadConfigItem]]) -> list[float]:
        """return an ordereded list of unique locations based on the load configuration list
        ex: load_config_list = [[{"pos":1.0,...},{"pos":3.0,...}],
                                [{"pos":2.0,...},{"pos":3.0,...}],
                                [{"pos":1.5,...},{"pos":2.5,...}]]
                return = [1.0, 1.5, 2.0, 2.5, 3.0]
        """
        unique = []
        for config in load_config_list:
            for info in config:
                if info["pos"] in unique:
                    continue
                unique.append(info["pos"])
        unique.sort()
        return unique

    def interp1d(self, l1: list[float], l2: list[float], pos: float) -> float:
        """1d linear interpolation for the vector components"""
        fac = (l2[1] - l1[1]) / (l2[0] - l1[0])
        v = l1[1] + fac * (pos - l1[0])
        return v

    def interpolate(
        self, pos: float, loadinfo: list[LoadConfigItem], start: int, end: int, key: Literal["load values"]
    ) -> np.ndarray:
        """interpolate the result vectors between load poits"""
        result = np.zeros(6)
        for i in range(6):
            value1 = [loadinfo[start]["pos"], loadinfo[start][key][i]]  # [position, force_component]
            value2 = [loadinfo[end]["pos"], loadinfo[end][key][i]]  #      [position, force_component]
            result[i] = self.interp1d(value1, value2, pos)  #             interpolated [position, force_component]
        return result

    def get_before_and_after(self, pos: float, load_config_list: list[list[LoadConfigItem]]) -> dict[str, list[float]]:
        """get total values for forces and moments before and after the position
        example:
            pos = 2.0
            load_config_list = [[{"pos":1.0,  "descr":"start, "load values":[1,0,0,0,0,0]},
                                 {"pos":3.0,  "descr":"end, "load values":[3,0,0,0,0,0]}],
                                [{"pos":2.0,  "descr":"start, "load values":[1,0,0,0,0,0]},
                                 {"pos":3.0,  "descr":"end, "load values":[1,0,0,0,0,0]}],
                                [{"pos":1.5,  "descr":"start, "load values":[1,0,0,0,0,0]},
                                 {"pos":2.5,  "descr":"end, "load values":[1,0,0,0,0,0]}],
            return = {
                        "before": [3,0,0,0,0,0],  ->(fx, fy, fz, mx, my, mz)
                        " after": [4,0,0,0,0,0]   ->(fx, fy, fz, mx, my, mz)
                    }
        """
        load_before = np.zeros(6)
        load_after = np.zeros(6)

        for config in load_config_list:
            if pos < config[0]["pos"] or pos > config[-1]["pos"]:
                continue
            start = 0
            end = len(config) - 1
            while end - start > 0:
                if pos < config[start]["pos"] or pos > config[end]["pos"]:
                    break
                if config[start]["pos"] == pos:
                    if config[start]["descr"] in ["start", "middle"]:
                        load_after += config[start]["load values"]

                    elif config[start]["descr"] in ["end", "middle"]:
                        load_before += config[start]["load values"]

                elif config[end]["pos"] == pos:
                    if config[end]["descr"] in ["start", "middle"]:
                        load_after += config[end]["load values"]

                    elif config[end]["descr"] in ["end", "middle"]:
                        load_before += config[end]["load values"]

                elif end - start == 1:
                    load_before += self.interpolate(pos, config, start, end, "load values")
                    load_after += self.interpolate(pos, config, start, end, "load values")
                start += 1
                end -= 1
        return_value = {"before": load_before.tolist(), "after": load_after.tolist()}
        return return_value

    def parse_linear_loads_to_dict(
        self, activity_list: list[tuple[ifcopenshell.entity_instance, float]], element_rotation_matrix: np.ndarray
    ) -> ParsedLoad:
        """
        get load list
        activity_list: list of IfcStructuralCurveAction or IfcStructuralCurveReaction
                        applied in the structural curve member
        global_to_local: transformation matrix from global coordinates to local coordinetes
        return: dict{
                    "constant force": (fx,fy,fz,mx,my,mz),	-> sum of linear loads applied with
                                                                constant distribution
                    "quadratic force": (fx,fy,fz,mx,my,mz),	-> sum of linear loads applied with
                                                                quadratic distribution
                    "sinus force": (fx,fy,fz,mx,my,mz),		-> sum of linear loads applied with
                                                                sinus distribution
                    "linear load configuration": list				-> list of load configurations for linear
                                                                and polyline distributions of linear loads
                    }
        description of "linear load configuration":
        list[							-> one item (list)for each IfcStructuralCurveAction applied in the member
                                            with IfcStructuralLoadConfiguration as the applied load
            list[						-> one item (dict) for each item found in the
                                            Locations attribute of IfcLoadConfiguration
                dict{
                    "pos": float,		-> local position along curve length
                    "descr": string,	-> describe if the item is at the start, middle or end of the list
                    "load values": Array,	-> linear force applied at that point
                    }
                ]
            ]
        """
        constant = np.zeros(6)
        quadratic = np.zeros(6)
        sinus = np.zeros(6)
        linear_load_configurations = []
        point_load_configurations = []

        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get(), "LENGTHUNIT")

        def get_load_values(load, transform_matrix, factor=1.0):
            result = np.zeros(6)
            keys = ["LinearForceX", "LinearForceY", "LinearForceZ", "LinearMomentX", "LinearMomentY", "LinearMomentZ"]
            for i, key in enumerate(keys):
                value = 0 if getattr(load, key, 0) is None else getattr(load, key, 0)
                result[i] += value * factor
            return transform_matrix @ result

        for item in activity_list:
            activity = item[0]
            factor = item[1]
            load = activity.AppliedLoad

            transform_3by3 = self.get_activity_transform_matrix(activity, element_rotation_matrix)
            transform_6by6 = np.zeros((6, 6))
            transform_6by6[0:3, 0:3] = transform_3by3
            transform_6by6[3:6, 3:6] = transform_3by3

            # values for linear loads
            if load.is_a("IfcStructuralLoadConfiguration"):
                locations = getattr(load, "Locations", [])
                values = [l for l in getattr(load, "Values", None) if l.is_a() == "IfcStructuralLoadLinearForce"]
                config_list = []
                for i, l in enumerate(values):
                    load_values = get_load_values(l, transform_6by6, factor)
                    if i == 0:
                        descr = "start"
                    elif i == len(values) - 1:
                        descr = "end"
                    else:
                        descr = "middle"
                    config_list.append(
                        {"pos": locations[i][0] * unit_scale, "descr": descr, "load values": load_values}
                    )
                linear_load_configurations.append(config_list)

                # load configurations with point loads
                values = [l for l in getattr(load, "Values", None) if l.is_a() == "IfcStructuralLoadSingleForce"]
                attr_list = ["ForceX", "ForceY", "ForceZ", "MomentX", "MomentY", "MomentZ"]
                config_list = []
                for i, val in enumerate(values):
                    result_list = [0, 0, 0, 0, 0, 0]
                    for j, attr in enumerate(attr_list):
                        value = 0 if getattr(val, attr, 0) is None else getattr(val, attr, 0)
                        result_list[j] += value * factor
                    config_list.append({"pos": locations[i][0] * unit_scale, "values": result_list})
                point_load_configurations.append(config_list)

            else:
                load_values = get_load_values(load, transform_6by6, factor)
                if "CONST" == getattr(activity, "PredefinedType", None) or activity.is_a("IfcStructuralLinearAction"):
                    constant += load_values
                elif "PARABOLA" == getattr(activity, "PredefinedType", None):
                    quadratic += load_values
                elif "SINUS" == getattr(activity, "PredefinedType", None):
                    sinus += load_values
        return_value = {
            "constant force": constant.tolist(),
            "quadratic force": quadratic.tolist(),
            "sinus force": sinus.tolist(),
            "linear load configuration": linear_load_configurations,
            "point load configuration": point_load_configurations,
        }
        return return_value
