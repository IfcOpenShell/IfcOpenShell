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

import bpy
import bmesh
import numpy as np
from math import sin
from mathutils import Vector
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.attribute
import ifcopenshell.util.unit as ifcunit
import bonsai.tool as tool
from bonsai.bim.ifc import IfcStore
from bonsai.bim.module.structural.shader import DecorationShader
from typing import Literal, TypedDict, Iterable

MemberInfo = TypedDict(
    "MemberInfo",
    {"member": ifcopenshell.entity_instance, "activities": list[tuple[ifcopenshell.entity_instance, float]]},
)

LoadConfigItem = TypedDict(
    "LoadConfigItem", {"pos": float, "descr": Literal["start", "end", "middle"], "load values": np.ndarray}
)

DiscreteConfigItem = TypedDict("DiscreteConfigItem", {"pos": float, "values": list[float]})

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
LoadByDirection = TypedDict(
    "LoadByDirection", {"constant": float, "quadratic": float, "sinus": float, "polyline": list[list[float]]}
)

ProcessedLoad = TypedDict(
    "ProcessedLoad",
    {"linear loads": LoadByDirection, "max linear load": float, "discrete loads": list[list[DiscreteConfigItem]]},
)


class ShaderInfo:
    def __init__(self) -> None:
        self.is_empty = True
        self.shader = DecorationShader()
        self.curve_members: dict[str, MemberInfo] = {}
        self.point_members: dict[str, MemberInfo] = {}
        self.surface_members: dict[str, MemberInfo] = {}
        self.text_info = []
        self.info = []
        self.force_unit = ""
        self.moment_unit = ""
        self.linear_force_unit = ""
        self.linear_moment_unit = ""
        self.planar_force_unit = ""

    def update(self) -> None:
        self.info = []
        self.text_info = []
        self.curve_members = {}
        self.point_members = {}
        self.surface_members = {}
        self.get_force_units()
        self.get_strucutural_elements_and_activities()
        self.get_linear_loads()
        self.get_point_loads()
        self.get_planar_loads()
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

        length_units = [u for u in tool.Ifc.get().by_type("IfcNamedUnit") if u.UnitType == "LENGTHUNIT"]
        force_units = [u for u in tool.Ifc.get().by_type("IfcNamedUnit") if u.UnitType == "FORCEUNIT"]
        linear_force_units = [u for u in tool.Ifc.get().by_type("IfcDerivedUnit") if u.UnitType == "LINEARFORCEUNIT"]
        linear_moment_units = [u for u in tool.Ifc.get().by_type("IfcDerivedUnit") if u.UnitType == "LINEARMOMENTUNIT"]
        planar_force_units = [u for u in tool.Ifc.get().by_type("IfcDerivedUnit") if u.UnitType == "PLANARFORCEUNIT"]

        conversion_force_unit = [u for u in force_units if u.is_a("IfcConversionBasedUnit")]
        if len(conversion_force_unit) == 0:
            conversion_force_unit.append(force_units[0])
        self.force_unit = ifcunit.get_unit_symbol(conversion_force_unit[0])

        conversion_length_unit = [u for u in length_units if u.is_a("IfcConversionBasedUnit")]
        if len(conversion_length_unit) == 0:
            conversion_length_unit.append(length_units[0])
        length_unit = ifcunit.get_unit_symbol(conversion_length_unit[0])
        self.moment_unit = self.force_unit + "." + length_unit

        first = ""
        second = ""
        for e in linear_force_units[0].Elements:
            if e.Unit.UnitType == "FORCEUNIT":
                first = ifcunit.get_unit_symbol(e.Unit)
            if e.Unit.UnitType == "LENGTHUNIT":
                second = ifcunit.get_unit_symbol(e.Unit)
        self.linear_force_unit = first + "/" + second

        first = ""
        second = ""
        for e in linear_moment_units[0].Elements:
            if e.Unit.UnitType == "FORCEUNIT":
                first = ifcunit.get_unit_symbol(e.Unit)
            if e.Unit.UnitType == "LENGTHUNIT":
                second = ifcunit.get_unit_symbol(e.Unit)
        self.linear_moment_unit = first + "." + second + "/" + second

        first = ""
        second = ""
        for e in planar_force_units[0].Elements:
            if e.Unit.UnitType == "FORCEUNIT":
                first = ifcunit.get_unit_symbol(e.Unit)
            if e.Unit.UnitType == "LENGTHUNIT":
                second = ifcunit.get_unit_symbol(e.Unit) + "2"
            if e.Unit.UnitType == "AREAUNIT":
                second = ifcunit.get_unit_symbol(e.Unit)
        self.planar_force_unit = first + "/" + second

    def get_strucutural_elements_and_activities(self) -> None:
        """fills self.point_members, self.curve_members and self.surface_members dictionaries"""

        def populate_members_dict(
            dict_name: Literal["point_members", "curve_members", "surface_members"],
            element: ifcopenshell.entity_instance,
            activity: ifcopenshell.entity_instance,
            factor: float,
        ) -> None:
            """
            fills self.point_members, self.curve_members and self.surface_members dictionaries
            thoses dicts will contain the strucutural member global id as key and a second dict as value
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

        props = bpy.context.scene.BIMStructuralProperties
        group_definition_id = int(props.load_group_to_show)
        file = IfcStore.get_file()
        groups = [file.by_id(group_definition_id)]
        recursive_subgroups(groups, 10, props.activity_type)

    def get_planar_loads(self) -> None:
        """get the necessary information to render the planar load representation in 3D and its text information"""

        list_of_surfaces = self.surface_members
        shader = self.shader.new("PLANAR LOAD")
        maximum = 0
        for value in list_of_surfaces.values():
            surf = value["member"]
            activity_list = value["activities"]
            if len(activity_list) == 0:
                continue
            rotation = self.get_surface_member_rotation(surf)
            values = self.get_planar_loads_values(activity_list, rotation)
            if maximum == 0:
                maximum = max([abs(float(i)) for i in values])
                if maximum == 0:
                    continue
            props = bpy.context.scene.BIMStructuralProperties
            reference_frame = props.reference_frame
            orientation = np.eye(3)
            if reference_frame == "LOCAL_COORDS":
                orientation = rotation
            blender_object: bpy.types.Object = IfcStore.get_element(getattr(surf, "GlobalId", None))
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
        values = np.zeros((3))
        for item in activity_list:
            activity = item[0]
            factor = item[1]
            load = activity.AppliedLoad
            temp = np.zeros((3))
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
        placement = ifcopenshell.util.placement.get_axis2placement(repr_item.FaceSurface.Position)
        rotation = placement[0:3, 0:3]
        return rotation

    def get_point_connection_rotation(self, point_connection: ifcopenshell.entity_instance) -> np.ndarray:
        """returns the rotation matrix of a structural point connection"""
        if point_connection.ConditionCoordinateSystem is not None:
            placement = ifcopenshell.util.placement.get_axis2placement(point_connection.ConditionCoordinateSystem)
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
        props = bpy.context.scene.BIMStructuralProperties
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
            activity_list = value["activities"]
            if len(activity_list) == 0:
                continue
            blender_object = IfcStore.get_element(getattr(conn, "GlobalId", None))
            if blender_object.type == "MESH":
                conn_location = blender_object.matrix_world @ blender_object.data.vertices[0].co
                rotation = self.get_point_connection_rotation(conn)
                loads = self.get_point_loads_values(activity_list, rotation)
                self.get_point_shader_args(loads, conn_location, rotation)

    def get_point_shader_args(self, loads: Iterable, location: np.ndarray, rotation: np.ndarray) -> None:
        """get the args to the point shader"""
        location = np.array(location)
        indices = []
        direction_dict = {
            "fx": (np.array((1, 0, 0)), np.array((0, 1, 0)), np.array((0, 0, 1))),
            "fy": (np.array((0, 1, 0)), np.array((1, 0, 0)), np.array((0, 0, 1))),
            "fz": (np.array((0, 0, 1)), np.array((0, 1, 0)), np.array((1, 0, 0))),
            "mx": (np.array((0, 1, 0)), np.array((0, 0, 1))),
            "my": (np.array((1, 0, 0)), np.array((0, 0, 1))),
            "mz": (np.array((1, 0, 0)), np.array((0, 1, 0))),
        }
        keys = ["fx", "fy", "fz", "mx", "my", "mz"]
        props = bpy.context.scene.BIMStructuralProperties
        reference_frame = props.reference_frame
        if reference_frame == "LOCAL_COORDS":
            for key in keys:
                tup = direction_dict[key]
                li = []
                for item in tup:
                    li.append(rotation @ item)
                direction_dict[key] = li

        for i, key in enumerate(keys):
            if loads[i] == 0:
                continue
            color = (1, 0, 0, 1)
            if i in [1, 4]:
                color = (0, 1, 0, 1)
            elif i in [2, 5]:
                color = (0, 0, 1, 1)
            d1 = -(direction_dict[key][0] * loads[i])
            d1 = d1 / np.linalg.norm(d1)
            if i < 3:
                d2 = direction_dict[key][1]
                d3 = direction_dict[key][2]
                p1 = location
                p2 = location + d1 + d2
                p3 = location + d1 - d2
                p4 = location + d1 + d3
                p5 = location + d1 - d3
                position = [p1, p2, p3, p4, p5]
                indices = [(0, 1, 2), (0, 3, 4)]
                c1 = (0, 0, 0)
                c2 = (1, 1, 0)
                c3 = (-1, 1, 0)
                coords_for_shader = [c1, c2, c3, c2, c3]
                shader = self.shader.new("SINGLE FORCE")
                self.info.append(
                    {
                        "shader": shader,
                        "args": {"position": position, "coord": coords_for_shader},
                        "indices": indices,
                        "uniforms": [["color", color], ["spacing", 0.2]],
                    }
                )
                self.text_info.append({"position": location + d1, "text": f"{loads[i]:.2f} {self.force_unit}"})
            else:
                d2 = d2 = direction_dict[key][1]
                p1 = location - d2
                p2 = location + d1 + d2
                p3 = location - d1 + d2
                position = [p1, p2, p3]
                indices = [(0, 1, 2)]
                c1 = (-1, 0, 0)
                c2 = (1, 1, 0)
                c3 = (1, -1, 0)
                coords_for_shader = [c1, c2, c3]
                shader = self.shader.new("SINGLE MOMENT")
                self.info.append(
                    {
                        "shader": shader,
                        "args": {"position": position, "coord": coords_for_shader},
                        "indices": indices,
                        "uniforms": [["color", color]],
                    }
                )
                self.text_info.append(
                    {"position": location + 0.25 * (d1 + d2), "text": f"{loads[i]:.2f} {self.moment_unit}"}
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
            temp = np.zeros(6)
            for i, attr in enumerate(attr_list):
                value = 0 if getattr(load, attr, 0) is None else getattr(load, attr, 0)
                temp[i] += value * factor
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
            activity_list = value["activities"]
            if len(activity_list) == 0:
                continue

            blender_object = IfcStore.get_element(getattr(member, "GlobalId", None))

            start_co = blender_object.matrix_world @ blender_object.data.vertices[0].co
            end_co = blender_object.matrix_world @ blender_object.data.vertices[1].co
            x_axis = Vector(end_co - start_co).normalized()
            z_direction = getattr(member, "Axis")
            # local coordinates
            z_axis = Vector(getattr(z_direction, "DirectionRatios", None)).normalized()
            y_axis = z_axis.cross(x_axis).normalized()
            z_axis = x_axis.cross(y_axis).normalized()
            rotation = self.get_curve_member_rotation(member)

            props = bpy.context.scene.BIMStructuralProperties
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
                    else Vector((-1, 0, 1)) if y_match else Vector((0, 1, 0)).cross(x_axis).normalized()
                ),
                "mz": (
                    y_axis
                    if is_local
                    else Vector((-1, 1, 0)) if z_match else Vector((0, 0, 1)).cross(x_axis).normalized()
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
                        self.get_point_shader_args(values, pos_vector, rotation)
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
                                    "text": f"{func:.2f} {unit}",
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
                                        "text": f"{func:.2f} {unit}",
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

    def interpolate(self, pos: float, loadinfo: list[LoadConfigItem], start: int, end: int, key: str) -> np.ndarray:
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
