# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2024 Bruno Perdigão <contact@brunopo.com>
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

from __future__ import annotations
import bpy
import copy
import math
import bmesh
import ifcopenshell
import ifcopenshell.api
import ifcopenshell.geom
import ifcopenshell.util.unit
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.type
import mathutils.geometry
import bonsai.core.type
import bonsai.core.root
import bonsai.core.geometry
import bonsai.core.model as core
import bonsai.tool as tool
from math import pi, sin, cos, degrees, tan, radians
from mathutils import Vector, Matrix, Quaternion
from bonsai.bim.module.model.opening import FilledOpeningGenerator
from bonsai.bim.module.model.decorator import PolylineDecorator
from bonsai.bim.module.geometry.decorator import ItemDecorator
from typing import Optional, Union, Literal, Any
from lark import Lark, Transformer


def create_bmesh_from_vertices(vertices, is_closed=False):
    bm = bmesh.new()

    new_verts = [bm.verts.new(v) for v in vertices]
    if is_closed:
        new_edges = [bm.edges.new((new_verts[i], new_verts[i + 1])) for i in range(len(new_verts) - 1)]
        new_edges.append(
            bm.edges.new((new_verts[-1], new_verts[0]))
        )  # Add an edge between the last an first point to make it closed.
    else:
        new_edges = [bm.edges.new((new_verts[i], new_verts[i + 1])) for i in range(len(new_verts) - 1)]

    bm.verts.index_update()
    bm.edges.index_update()
    return bm


def get_wall_preview_data(context, relating_type):
    # Get properties from object type
    model_props = tool.Model.get_model_props()
    direction_sense = model_props.direction_sense
    direction = 1
    if direction_sense == "NEGATIVE":
        direction = -1

    layers = tool.Model.get_material_layer_parameters(relating_type)
    if not layers["thickness"]:
        return
    thickness = layers["thickness"]
    thickness *= direction

    offset_type = model_props.offset_type_vertical
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
    offset = model_props.offset * unit_scale

    height = float(model_props.extrusion_depth)
    rl = float(model_props.rl1)
    x_angle = float(model_props.x_angle)
    if x_angle > radians(90) or x_angle < radians(-90):
        height *= -1
    angle_distance = height * tan(x_angle)
    thickness *= 1 / cos(x_angle)

    data = {}
    data["verts"] = []

    # Verts
    polyline_vertices = []
    polyline_data = context.scene.BIMPolylineProperties.insertion_polyline
    polyline_points = polyline_data[0].polyline_points if polyline_data else []
    if len(polyline_points) < 2:
        data = []
        return
    for point in polyline_points:
        polyline_vertices.append(Vector((point.x, point.y, point.z)))

    is_closed = False
    if (
        polyline_vertices[0].x == polyline_vertices[-1].x
        and polyline_vertices[0].y == polyline_vertices[-1].y
        and polyline_vertices[0].z == polyline_vertices[-1].z
    ):
        is_closed = True
        polyline_vertices.pop(-1)  # Remove the last point. The edges are going to inform that the shape is closed.

    bm_base = create_bmesh_from_vertices(polyline_vertices, is_closed)
    base_vertices = tool.Cad.offset_edges(bm_base, offset)
    offset_base_verts = tool.Cad.offset_edges(bm_base, thickness + offset)
    top_vertices = tool.Cad.offset_edges(bm_base, angle_distance + offset)
    offset_top_verts = tool.Cad.offset_edges(bm_base, angle_distance + thickness + offset)
    if is_closed:
        base_vertices.append(base_vertices[0])
        offset_base_verts.append(offset_base_verts[0])
        top_vertices.append(top_vertices[0])
        offset_top_verts.append(offset_top_verts[0])

    if offset_base_verts is not None:
        for v in base_vertices:
            data["verts"].append((v.co.x, v.co.y, v.co.z + rl))

        for v in offset_base_verts[::-1]:
            data["verts"].append((v.co.x, v.co.y, v.co.z + rl))

        for v in top_vertices:
            data["verts"].append((v.co.x, v.co.y, v.co.z + rl + height))

        for v in offset_top_verts[::-1]:
            data["verts"].append((v.co.x, v.co.y, v.co.z + rl + height))

    bm_base.free()

    # Edges and Tris
    points = []
    side_edges_1 = []
    side_edges_2 = []
    base_edges = []

    for i in range(len(data["verts"])):
        points.append(Vector(data["verts"][i]))

    n = len(points) // 2
    bottom_side_1 = [[i, (i + 1) % (n)] for i in range((n - 1) // 2)]
    bottom_side_2 = [[i, (i + 1) % (n)] for i in range(n // 2, n - 1)]
    bottom_connections = [[i, n - i - 1] for i in range(n // 2)]
    bottom_loop = bottom_connections + bottom_side_1 + bottom_side_2
    side_edges_1.extend(bottom_side_1)
    side_edges_2.extend(bottom_side_2)
    base_edges.extend(bottom_loop)

    upper_side_1 = [[i + n for i in edges] for edges in bottom_side_1]
    upper_side_2 = [[i + n for i in edges] for edges in bottom_side_2]
    upper_loop = [[i + n for i in edges] for edges in bottom_loop]
    side_edges_1.extend(upper_side_1)
    side_edges_2.extend(upper_side_2)
    base_edges.extend(upper_loop)

    loops = [side_edges_1, side_edges_2, base_edges]

    data["edges"] = []
    data["tris"] = []
    for i, group in enumerate(loops):
        bm = bmesh.new()

        new_verts = [bm.verts.new(v) for v in points]
        new_edges = [bm.edges.new((new_verts[e[0]], new_verts[e[1]])) for e in group]

        bm.verts.index_update()
        bm.edges.index_update()

        if i == 2:
            new_faces = bmesh.ops.contextual_create(bm, geom=bm.edges)
        new_faces = bmesh.ops.bridge_loops(bm, edges=bm.edges, use_pairs=True, use_cyclic=True)

        bm.verts.index_update()
        bm.edges.index_update()
        edges = [[v.index for v in e.verts] for e in bm.edges]
        tris = [[l.vert.index for l in loop] for loop in bm.calc_loop_triangles()]
        data["edges"].extend(edges)
        data["tris"].extend(tris)

    data["edges"] = list(set(tuple(e) for e in data["edges"]))
    data["tris"] = list(set(tuple(t) for t in data["tris"]))

    return data


def get_slab_preview_data(context, relating_type):
    model_props = tool.Model.get_model_props()
    x_angle = 0 if tool.Cad.is_x(model_props.x_angle, 0, tolerance=0.001) else model_props.x_angle
    direction_sense = model_props.direction_sense
    direction = 1
    if direction_sense == "NEGATIVE":
        direction = -1

    layers = tool.Model.get_material_layer_parameters(relating_type)
    if not layers["thickness"]:
        return
    thickness = layers["thickness"] * abs(1 / cos(x_angle))
    thickness *= direction

    offset_type = model_props.offset_type_horizontal
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
    offset = model_props.offset * abs(1 / cos(x_angle)) * unit_scale

    data = {}
    data["verts"] = []
    # Verts
    polyline_vertices = []
    polyline_data = context.scene.BIMPolylineProperties.insertion_polyline
    polyline_points = polyline_data[0].polyline_points if polyline_data else []
    if len(polyline_points) < 3:
        data = []
        return
    for point in polyline_points:
        polyline_vertices.append(Vector((point.x, point.y, point.z)))
    if x_angle:
        # Get vertices relative to the first polyline point as origin
        local_vertices = [v - Vector(polyline_vertices[0]) for v in polyline_vertices]
        # Make the transformation relative to the x_angle
        transformed_vertices = [Vector((v.x, v.y * (1 / cos(x_angle)), v.z)) for v in local_vertices]
        # Convert back to world origin
        polyline_vertices = [v + Vector(polyline_vertices[0]) for v in transformed_vertices]
    if offset != 0:
        polyline_vertices = [v + Vector((0, 0, offset)) for v in polyline_vertices]
    is_closed = True
    if (
        polyline_vertices[0].x == polyline_vertices[-1].x
        and polyline_vertices[0].y == polyline_vertices[-1].y
        and polyline_vertices[0].z == polyline_vertices[-1].z
    ):
        polyline_vertices.pop(-1)  # Remove the last point. The edges are going to inform that the shape is closed.
    bm = create_bmesh_from_vertices(polyline_vertices, is_closed)
    bm.verts.ensure_lookup_table()
    if x_angle:
        rot_mat = Matrix.Rotation(x_angle, 3, "X")
        if abs(x_angle) > (pi / 2):
            rot_mat = rot_mat @ Matrix.Scale(-1, 3, (0, 1, 0))
        bmesh.ops.rotate(bm, cent=Vector(bm.verts[0].co), verts=bm.verts, matrix=rot_mat)
    new_faces = bmesh.ops.contextual_create(bm, geom=bm.edges)
    new_faces = bmesh.ops.extrude_face_region(bm, geom=bm.edges[:] + bm.faces[:])
    new_verts = [e for e in new_faces["geom"] if isinstance(e, bmesh.types.BMVert)]
    new_faces = bmesh.ops.translate(bm, verts=new_verts, vec=(0.0, 0.0, thickness))
    bm.verts.index_update()
    bm.edges.index_update()
    verts = [tuple(v.co) for v in bm.verts]
    edges = [[v.index for v in e.verts] for e in bm.edges]
    tris = [[loop.vert.index for loop in triangles] for triangles in bm.calc_loop_triangles()]
    data["verts"] = verts
    data["edges"] = edges
    data["tris"] = tris
    return data


def get_vertical_profile_preview_data(
    context: bpy.types.Context, relating_type: ifcopenshell.entity_instance
) -> dict[str, Any]:
    material = ifcopenshell.util.element.get_material(relating_type)
    try:
        profile = material.MaterialProfiles[0].Profile
    except:
        return {}

    model_props = tool.Model.get_model_props()
    extrusion_depth = model_props.extrusion_depth
    cardinal_point = model_props.cardinal_point
    rot_mat = Quaternion()
    if relating_type.is_a("IfcBeamType"):
        y_rot = Quaternion((0.0, 1.0, 0.0), radians(90))
        z_rot = Quaternion((0.0, 0.0, 1.0), radians(90))
        rot_mat = y_rot @ z_rot
    # Get profile data
    settings = ifcopenshell.geom.settings()
    settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
    shape = ifcopenshell.geom.create_shape(settings, profile)

    verts = shape.verts
    if not verts:
        raise RuntimeError(f"Profile shape has no vertices, it probably is invalid: '{profile}'.")

    edges = shape.edges

    grouped_verts = [[verts[i], verts[i + 1], 0] for i in range(0, len(verts), 3)]
    grouped_edges = [[edges[i], edges[i + 1]] for i in range(0, len(edges), 2)]

    # Create offsets based on cardinal point
    min_x = min(v[0] for v in grouped_verts)
    max_x = max(v[0] for v in grouped_verts)
    min_y = min(v[1] for v in grouped_verts)
    max_y = max(v[1] for v in grouped_verts)

    x_offset = (max_x - min_x) / 2
    y_offset = (max_y - min_y) / 2

    match cardinal_point:
        case "1":
            grouped_verts = [(v[0] - x_offset, v[1] + y_offset, v[2]) for v in grouped_verts]
        case "2":
            grouped_verts = [(v[0], v[1] + y_offset, v[2]) for v in grouped_verts]
        case "3":
            grouped_verts = [(v[0] + x_offset, v[1] + y_offset, v[2]) for v in grouped_verts]
        case "4":
            grouped_verts = [(v[0] - x_offset, v[1], v[2]) for v in grouped_verts]
        case "5":
            grouped_verts = [(v[0], v[1], v[2]) for v in grouped_verts]
        case "6":
            grouped_verts = [(v[0] + x_offset, v[1], v[2]) for v in grouped_verts]
        case "7":
            grouped_verts = [(v[0] - x_offset, v[1] - y_offset, v[2]) for v in grouped_verts]
        case "8":
            grouped_verts = [(v[0], v[1] - y_offset, v[2]) for v in grouped_verts]
        case "9":
            grouped_verts = [(v[0] + x_offset, v[1] - y_offset, v[2]) for v in grouped_verts]

    # Create extrusion bmesh
    bm = bmesh.new()

    grouped_verts.append(grouped_verts[0])  # Close profile
    new_verts = [bm.verts.new(v) for v in grouped_verts]
    new_edges = [bm.edges.new((new_verts[i], new_verts[i + 1])) for i in range(len(grouped_verts) - 1)]

    bm.verts.index_update()
    bm.edges.index_update()

    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)

    new_faces = bmesh.ops.contextual_create(bm, geom=bm.edges)

    new_faces = bmesh.ops.extrude_face_region(bm, geom=bm.faces, use_dissolve_ortho_edges=True)
    new_verts = [e for e in new_faces["geom"] if isinstance(e, bmesh.types.BMVert)]
    new_faces = bmesh.ops.translate(bm, verts=new_verts, vec=(0.0, 0.0, extrusion_depth))

    bm.verts.index_update()
    bm.edges.index_update()
    tris = [[loop.vert.index for loop in triangles] for triangles in bm.calc_loop_triangles()]

    # Calculate rotation, mouse position, angle and cardinal point
    snap_prop = context.scene.BIMPolylineProperties.snap_mouse_point[0]
    mouse_point = Vector((snap_prop.x, snap_prop.y, snap_prop.z))
    data = {}

    verts = [tuple(v.co) for v in bm.verts]
    verts = [tuple(rot_mat @ Vector(v)) for v in verts]
    verts = [tuple(Vector(v) + mouse_point) for v in verts]
    min_z = min(v.co.z for v in bm.verts)
    max_z = max(v.co.z for v in bm.verts)
    # Add axis verts
    verts.append(tuple(mouse_point))
    verts.append(tuple(mouse_point + Vector((0, 0, max_z))))
    # Add only profile edges
    edges = []
    for edge in bm.edges:
        if (edge.verts[0].co.z == min_z and edge.verts[1].co.z == min_z) or (
            edge.verts[0].co.z == max_z and edge.verts[1].co.z == max_z
        ):
            edges.append(edge)
    # Add axis edge
    edges = [(edge.verts[0].index, edge.verts[1].index) for edge in edges]
    edges.append((len(verts) - 1, len(verts) - 2))
    data["verts"] = verts
    data["edges"] = edges
    data["tris"] = tris

    bm.free()

    return data


def get_horizontal_profile_preview_data(context, relating_type):
    material = ifcopenshell.util.element.get_material(relating_type)
    try:
        profile_curve = material.MaterialProfiles[0].Profile
    except:
        return {}

    model_props = tool.Model.get_model_props()
    cardinal_point = model_props.cardinal_point

    polyline_verts = []
    polyline_data = context.scene.BIMPolylineProperties.insertion_polyline
    polyline_points = polyline_data[0].polyline_points if polyline_data else []
    if len(polyline_points) < 2:
        return
    for point in polyline_points:
        polyline_verts.append(Vector((point.x, point.y, point.z)))
    polyline_edges = [(i, i + 1) for i in range(len(polyline_verts) - 1)]

    # Get profile shape
    settings = ifcopenshell.geom.settings()
    settings.set("dimensionality", ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS)
    shape = ifcopenshell.geom.create_shape(settings, profile_curve)

    verts = shape.verts
    if not verts:
        raise RuntimeError(f"Profile shape has no vertices, it probably is invalid: '{profile}'.")

    edges = shape.edges

    grouped_verts = [[verts[i], verts[i + 1], 0] for i in range(0, len(verts), 3)]
    grouped_edges = [[edges[i], edges[i + 1]] for i in range(0, len(edges), 2)]

    # Create offsets based on cardinal point
    min_x = min(v[0] for v in grouped_verts)
    max_x = max(v[0] for v in grouped_verts)
    min_y = min(v[1] for v in grouped_verts)
    max_y = max(v[1] for v in grouped_verts)

    x_offset = (max_x - min_x) / 2
    y_offset = (max_y - min_y) / 2

    match cardinal_point:
        case "1":
            grouped_verts = [(v[0] - x_offset, v[1] + y_offset, v[2]) for v in grouped_verts]
        case "2":
            grouped_verts = [(v[0], v[1] + y_offset, v[2]) for v in grouped_verts]
        case "3":
            grouped_verts = [(v[0] + x_offset, v[1] + y_offset, v[2]) for v in grouped_verts]
        case "4":
            grouped_verts = [(v[0] - x_offset, v[1], v[2]) for v in grouped_verts]
        case "5":
            grouped_verts = [(v[0], v[1], v[2]) for v in grouped_verts]
        case "6":
            grouped_verts = [(v[0] + x_offset, v[1], v[2]) for v in grouped_verts]
        case "7":
            grouped_verts = [(v[0] - x_offset, v[1] - y_offset, v[2]) for v in grouped_verts]
        case "8":
            grouped_verts = [(v[0], v[1] - y_offset, v[2]) for v in grouped_verts]
        case "9":
            grouped_verts = [(v[0] + x_offset, v[1] - y_offset, v[2]) for v in grouped_verts]

    data = {}
    data["verts"] = []
    data["edges"] = []
    data["tris"] = []

    grouped_verts = [(v) for v in grouped_verts]

    all_bm = bmesh.new()
    for i in range(len(polyline_verts) - 1):
        mesh = bpy.data.meshes.new("TempMesh")
        # Create the initial mesh from the profile verts
        bm = create_bmesh_from_vertices(grouped_verts, is_closed=True)
        bm.verts.ensure_lookup_table()
        # Creates the clipping plane formed by two segments.
        # The first one is for the profile start, based on the current and previous segment of the polyline.
        # The second is for the profile end, based on the current and the next segment.
        if i == 0:
            d = (polyline_verts[i + 1] - polyline_verts[i]).normalized()
            clip_start = d
        else:
            d1 = (polyline_verts[i] - polyline_verts[i - 1]).normalized()
            d2 = (polyline_verts[i] - polyline_verts[i + 1]).normalized()
            clip_start = (d1 - d2).normalized()

        if i == len(polyline_verts) - 2:
            d = (polyline_verts[i + 1] - polyline_verts[i]).normalized()
            clip_end = d
        else:
            d1 = (polyline_verts[i + 1] - polyline_verts[i]).normalized()
            d2 = (polyline_verts[i + 1] - polyline_verts[i + 2]).normalized()
            clip_end = (d1 - d2).normalized()

        # Rotates the profile face to the right direction
        direction = polyline_verts[i + 1] - polyline_verts[i]
        position = polyline_verts[i]
        rotation_matrix = direction.to_track_quat("Z", "Y").to_matrix().to_4x4()
        bmesh.ops.transform(bm, verts=bm.verts, matrix=rotation_matrix)
        bmesh.ops.translate(bm, verts=bm.verts, vec=position)
        bmesh.ops.translate(bm, verts=bm.verts, vec=-direction)

        # Extrude and move the new face
        last_face = bmesh.ops.extrude_face_region(bm, geom=bm.edges[:] + bm.faces[:])
        new_verts = [e for e in last_face["geom"] if isinstance(e, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=new_verts, vec=direction * 3)
        # Apply the cutting planes
        cut = bmesh.ops.bisect_plane(
            bm,
            geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
            plane_co=polyline_verts[i],
            plane_no=clip_start,
            clear_inner=True,
        )
        bm.verts.index_update()
        bm.edges.index_update()
        cut = bmesh.ops.bisect_plane(
            bm,
            geom=bm.verts[:] + bm.edges[:] + bm.faces[:],
            plane_co=polyline_verts[i + 1],
            plane_no=clip_end,
            clear_outer=True,
        )

        bm.to_mesh(mesh)
        bm.free()
        mesh.update()
        all_bm.from_mesh(mesh)
        bpy.data.meshes.remove(bpy.data.meshes["TempMesh"])

    # It's necessary to add the mesh to an object to get the expected result.
    mesh = bpy.data.meshes.new("TempMesh2")
    all_bm.to_mesh(mesh)
    all_bm.free()
    obj = bpy.data.objects.new("TempObj", mesh)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bpy.data.meshes.remove(bpy.data.meshes["TempMesh2"])

    verts = [tuple(v.co) for v in bm.verts]
    edges = [[v.index for v in e.verts] for e in bm.edges]
    tris = [[loop.vert.index for loop in triangles] for triangles in bm.calc_loop_triangles()]
    data["verts"] = verts
    data["edges"] = edges
    data["tris"] = tris
    bm.free()
    return data


def get_generic_product_preview_data(context, relating_type):
    model_props = tool.Model.get_model_props()
    if relating_type.is_a("IfcDoorType"):
        rl = float(model_props.rl1)
    elif relating_type.is_a("IfcWindowType"):
        rl = float(model_props.rl2)
    else:
        rl = 0
    snap_prop = context.scene.BIMPolylineProperties.snap_mouse_point[0]
    default_container_elevation = tool.Root.get_default_container_elevation()
    mouse_point = Vector((snap_prop.x, snap_prop.y, default_container_elevation))
    snap_obj = bpy.data.objects.get(snap_prop.snap_object)
    snap_element = tool.Ifc.get_entity(snap_obj)
    rot_mat = Quaternion()
    if snap_element and snap_element.is_a("IfcWall"):
        rot_mat = snap_obj.matrix_world.to_quaternion()

    obj_type = tool.Ifc.get_object(relating_type)
    if obj_type.data:
        data = ItemDecorator.get_obj_data(obj_type)
        data["verts"] = [tuple(obj_type.matrix_world.inverted() @ Vector(v)) for v in data["verts"]]
        data["verts"] = [tuple(rot_mat @ (Vector((v[0], v[1], (v[2] + rl)))) + mouse_point) for v in data["verts"]]

        return data


class PolylineOperator:
    # TODO Fill doc strings
    """ """

    objs_2d_bbox: list[tuple[bpy.types.Object, list[float]]]

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        return context.space_data.type == "VIEW_3D"

    def __init__(self):
        self.mousemove_count = 0
        self.action_count = 0
        self.visible_objs = []
        self.objs_2d_bbox = []
        self.number_options = {
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            " ",
            ".",
            "+",
            "-",
            "*",
            "/",
            "'",
            '"',
            "=",
        }
        self.number_input = []
        self.number_output = ""
        self.number_is_negative = False
        self.input_options = ["D", "A", "X", "Y"]
        self.input_type = None
        self.input_value_xy = [None, None]
        self.input_ui = tool.Polyline.create_input_ui(input_options=self.input_options)
        self.is_typing = False
        self.snap_angle = None
        self.snapping_points = []
        self.instructions = {
            "Cycle Input": {"icons": True, "keys": ["EVENT_TAB"]},
            "Distance Input": {"icons": True, "keys": ["EVENT_D"]},
            "Angle Lock": {"icons": True, "keys": ["EVENT_A"]},
            "Increment Angle": {"icons": True, "keys": ["EVENT_SHIFT", "MOUSE_MMB_SCROLL"]},
            "Modify Snap Point": {"icons": True, "keys": ["EVENT_M"]},
            "Close Polyline": {"icons": True, "keys": ["EVENT_C"]},
            "Remove Point": {"icons": True, "keys": ["EVENT_BACKSPACE"]},
        }

        self.info = [
            "Axis: ",
            "Plane: ",
            "Snap: ",
        ]

        self.tool_state = tool.Polyline.create_tool_state()

    def recalculate_inputs(self, context: bpy.types.Context) -> Union[bool, None]:
        if self.number_input:
            is_valid, self.number_output = tool.Polyline.validate_input(self.number_output, self.input_type)
            self.input_ui.set_value(self.input_type, self.number_output)
            if not is_valid:
                self.report({"WARNING"}, "The number typed is not valid.")
                return is_valid
            else:
                if self.input_type in {"X", "Y", "Z"}:
                    tool.Polyline.calculate_distance_and_angle(context, self.input_ui, self.tool_state)
                elif self.input_type in {"D", "A"}:
                    tool.Polyline.calculate_x_y_and_z(context, self.input_ui, self.tool_state)
                    tool.Polyline.calculate_distance_and_angle(context, self.input_ui, self.tool_state)
                else:
                    self.input_ui.set_value(self.input_type, self.number_output)
            tool.Blender.update_viewport()
            return is_valid

    def choose_axis(self, event: bpy.types.Event, x: bool = True, y: bool = True, z: bool = False) -> None:
        options = {"X", "Y"}
        if z:
            options = {"X", "Y", "Z"}
        if not event.shift and event.value == "PRESS" and event.type in options:
            self.tool_state.axis_method = event.type if self.tool_state.axis_method != event.type else None
            if self.tool_state.axis_method is not None:
                self.tool_state.lock_axis = True
            else:
                self.tool_state.lock_axis = False
            PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
            tool.Blender.update_viewport()

    def choose_plane(self, event: bpy.types.Event, x: bool = True, y: bool = True, z: bool = True) -> None:
        if x:
            if event.shift and event.value == "PRESS" and event.type == "X":
                self.tool_state.use_default_container = False
                self.tool_state.plane_method = "YZ" if self.tool_state.plane_method != "YZ" else None
                self.tool_state.axis_method = None
                tool.Blender.update_viewport()

        if y:
            if event.shift and event.value == "PRESS" and event.type == "Y":
                self.tool_state.use_default_container = False
                self.tool_state.plane_method = "XZ" if self.tool_state.plane_method != "XZ" else None
                self.tool_state.axis_method = None
                tool.Blender.update_viewport()

        if z:
            if event.shift and event.value == "PRESS" and event.type == "Z":
                self.tool_state.use_default_container = False
                self.tool_state.plane_method = "XY" if self.tool_state.plane_method != "XY" else None
                self.tool_state.axis_method = None
                tool.Blender.update_viewport()

    def handle_instructions(
        self, context: bpy.types.Context, custom_instructions: dict = {}, custom_info: str = "", overwrite: bool = False
    ) -> None:
        self.info = [
            f"Axis: {self.tool_state.axis_method}",
            f"Plane: {self.tool_state.plane_method}",
            f"Snap: {self.snapping_points[0]['type']}",
        ]
        instructions = self.instructions | custom_instructions if custom_instructions else self.instructions
        infos = self.info + custom_info if custom_info else self.info

        if overwrite:
            instructions = custom_instructions
            infos = custom_info

        def draw_instructions(self: bpy.types.Header, context: bpy.types.Context) -> None:
            for action, settings in instructions.items():
                if settings["icons"]:
                    for key in settings["keys"]:
                        self.layout.label(text="", icon=key)
                    self.layout.label(text=action)
                else:
                    key = settings["keys"][0]
                    self.layout.label(text=key + action)

            if infos:
                self.layout.label(text="|")
                for info in infos:
                    self.layout.label(text=info)

        context.workspace.status_text_set(draw_instructions)

    def handle_lock_axis(self, context: bpy.types.Context, event: bpy.types.Event) -> None:
        if event.value == "PRESS" and event.type == "A":
            self.tool_state.lock_axis = False if self.tool_state.lock_axis else True
            if self.tool_state.lock_axis:
                self.tool_state.snap_angle = self.input_ui.get_number_value("WORLD_ANGLE")
                # Round to the closest 5
                self.tool_state.snap_angle = round(self.tool_state.snap_angle / 5) * 5

        if event.shift and event.type in {"WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
            self.tool_state.lock_axis = True
            self.tool_state.snap_angle = self.input_ui.get_number_value("WORLD_ANGLE")
            # Round to the closest 5
            self.tool_state.snap_angle = round(self.tool_state.snap_angle / 5) * 5
            if event.type in {"WHEELUPMOUSE"}:
                self.tool_state.snap_angle += 5
            else:
                self.tool_state.snap_angle -= 5
            self.handle_mouse_move(context, event)
            detected_snaps = tool.Snap.detect_snapping_points(context, event, self.objs_2d_bbox, self.tool_state)
            self.snapping_points = tool.Snap.select_snapping_points(context, event, self.tool_state, detected_snaps)
            tool.Polyline.calculate_distance_and_angle(context, self.input_ui, self.tool_state)
            PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
            tool.Blender.update_viewport()

    def handle_keyboard_input(self, context: bpy.types.Context, event: bpy.types.Event) -> None:

        if self.tool_state.is_input_on and event.value == "PRESS" and event.type == "TAB":
            self.recalculate_inputs(context)
            index = self.input_options.index(self.input_type)
            size = len(self.input_options)
            self.input_type = self.input_options[((index + 1) % size)]
            self.tool_state.input_type = self.input_options[((index + 1) % size)]
            self.tool_state.mode = "Select"
            self.is_typing = False
            self.number_input = self.input_ui.get_formatted_value(self.input_type)
            self.number_input = list(self.number_input)
            self.number_output = "".join(self.number_input)
            self.input_ui.set_value(self.input_type, self.number_output)
            PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
            tool.Blender.update_viewport()

        if not self.tool_state.is_input_on and event.value == "RELEASE" and event.type == "TAB":
            self.recalculate_inputs(context)
            self.tool_state.mode = "Select"
            self.tool_state.is_input_on = True
            self.input_type = "D"
            self.tool_state.input_type = "D"
            self.is_typing = False
            self.number_input = self.input_ui.get_formatted_value(self.input_type)
            self.number_input = list(self.number_input)
            self.number_output = "".join(self.number_input)
            self.input_ui.set_value(self.input_type, self.number_output)
            PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
            tool.Blender.update_viewport()

        if not self.tool_state.is_input_on and event.ascii in self.number_options:
            self.recalculate_inputs(context)
            self.tool_state.mode = "Edit"
            self.tool_state.is_input_on = True
            self.input_type = "D"
            self.tool_state.input_type = "D"
            PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
            tool.Blender.update_viewport()

        if event.value == "RELEASE" and event.type == "D":
            self.recalculate_inputs(context)
            self.tool_state.mode = "Edit"
            self.tool_state.is_input_on = True
            self.input_type = event.type
            self.tool_state.input_type = event.type
            self.input_ui.set_value(self.input_type, "")
            PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
            tool.Blender.update_viewport()

        if self.input_type in self.input_options:
            if (event.ascii in self.number_options) or (event.value == "RELEASE" and event.type == "BACK_SPACE"):
                if not self.tool_state.mode == "Edit" and not (event.ascii == "=" or event.type == "BACK_SPACE"):
                    self.number_input = []

                if event.type == "BACK_SPACE":
                    if len(self.number_input) <= 1:
                        self.number_input = []
                    else:
                        self.number_input.pop(-1)
                elif event.ascii == "=":
                    if self.number_input and self.number_input[0] == "=":
                        self.number_input.pop(0)
                    else:
                        self.number_input.insert(0, "=")
                else:
                    self.number_input.append(event.ascii)

                if not self.number_input:
                    self.number_output = "0"

                self.tool_state.mode = "Edit"
                self.is_typing = True
                self.number_output = "".join(self.number_input)
                self.input_ui.set_value(self.input_type, self.number_output)
                PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
                tool.Blender.update_viewport()

    def handle_inserting_polyline(self, context: bpy.types.Context, event: bpy.types.Event) -> None:
        if not self.tool_state.is_input_on and event.value == "RELEASE" and event.type == "LEFTMOUSE":
            result = tool.Polyline.insert_polyline_point(self.input_ui, self.tool_state)
            if result:
                self.report({"WARNING"}, result)
            tool.Blender.update_viewport()

        if event.value == "PRESS" and event.type == "C":
            # Get the first point coordinates to close the polyline
            polyline_data = bpy.context.scene.BIMPolylineProperties.insertion_polyline
            polyline_points = polyline_data[0].polyline_points if polyline_data else []
            if len(polyline_points) > 2:
                first_point = polyline_points[0]
                last_point = polyline_points[-1]
                if not (
                    first_point.x == last_point.x and first_point.y == last_point.y and first_point.z == last_point.z
                ):
                    self.input_ui.set_value("X", first_point.x)
                    self.input_ui.set_value("Y", first_point.y)
                    if self.input_ui.get_number_value("Z") is not None:
                        self.input_ui.set_value("Z", first_point.z)
                    else:
                        self.input_ui.set_value("Z", 0)
            result = tool.Polyline.insert_polyline_point(self.input_ui, self.tool_state)
            if result:
                self.report({"WARNING"}, result)

            PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
            tool.Blender.update_viewport()

        if (
            self.tool_state.is_input_on
            and event.value == "RELEASE"
            and event.type in {"RET", "NUMPAD_ENTER", "RIGHTMOUSE"}
        ):
            is_valid = self.recalculate_inputs(context)
            if is_valid:
                result = tool.Polyline.insert_polyline_point(self.input_ui, self.tool_state)
                if result:
                    self.report({"WARNING"}, result)

            self.tool_state.mode = "Mouse"
            self.tool_state.is_input_on = False
            self.input_type = None
            self.tool_state.input_type = None
            self.number_input = []
            self.number_output = ""
            PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
            tool.Blender.update_viewport()

        if not self.tool_state.is_input_on:
            if event.value == "RELEASE" and event.type == "BACK_SPACE":
                tool.Polyline.remove_last_polyline_point()
                tool.Blender.update_viewport()

    def handle_snap_selection(self, context: bpy.types.Context, event: bpy.types.Event) -> None:
        if not self.tool_state.is_input_on and event.value == "PRESS" and event.type == "M":
            self.snapping_points = tool.Snap.modify_snapping_point_selection(
                self.snapping_points, lock_axis=self.tool_state.lock_axis
            )
            tool.Polyline.calculate_distance_and_angle(context, self.input_ui, self.tool_state)
            PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
            tool.Blender.update_viewport()

    def handle_cancelation(
        self, context: bpy.types.Context, event: bpy.types.Event
    ) -> Union[None, set[Literal["CANCELLED"]]]:
        if self.tool_state.is_input_on:
            if event.value == "RELEASE" and event.type in {"ESC", "LEFTMOUSE"}:
                self.recalculate_inputs(context)
                self.tool_state.mode = "Mouse"
                self.tool_state.is_input_on = False
                self.input_type = None
                self.tool_state.input_type = None
                PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
                tool.Blender.update_viewport()
        else:
            if event.value == "RELEASE" and event.type in {"ESC"}:
                self.tool_state.axis_method = None
                context.workspace.status_text_set(text=None)
                PolylineDecorator.uninstall()
                tool.Polyline.clear_polyline()
                tool.Blender.update_viewport()
                return {"CANCELLED"}

    def handle_mouse_move(
        self, context: bpy.types.Context, event: bpy.types.Event, should_round: bool = False
    ) -> Union[None, set[Literal["RUNNING_MODAL"]]]:
        if not self.tool_state.is_input_on:
            if event.type == "MOUSEMOVE" or event.type == "INBETWEEN_MOUSEMOVE":
                self.mousemove_count += 1
                self.tool_state.mode = "Mouse"
                self.tool_state.is_input_on = False
                self.input_type = None
                self.tool_state.input_type = None
                PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
                tool.Snap.clear_snapping_ref()
                tool.Blender.update_viewport()
            else:
                self.mousemove_count = 0

            if self.mousemove_count == 2:
                self.objs_2d_bbox = []
                for obj in self.visible_objs:
                    if bbox_2d := tool.Raycast.get_on_screen_2d_bounding_boxes(context, obj):
                        self.objs_2d_bbox.append(bbox_2d)

            if self.mousemove_count > 3:
                detected_snaps = tool.Snap.detect_snapping_points(context, event, self.objs_2d_bbox, self.tool_state)
                self.snapping_points = tool.Snap.select_snapping_points(context, event, self.tool_state, detected_snaps)

                if self.snapping_points[0]["type"] not in {"Plane", "Axis"}:
                    should_round = False

                tool.Polyline.calculate_distance_and_angle(
                    context, self.input_ui, self.tool_state, should_round=should_round
                )
                if should_round:
                    tool.Polyline.calculate_x_y_and_z(context, self.input_ui, self.tool_state)

                tool.Blender.update_viewport()
                return {"RUNNING_MODAL"}

    def get_product_preview_data(self, context: bpy.types.Context, relating_type: ifcopenshell.entity_isntance):
        if tool.Model.get_usage_type(relating_type) == "PROFILE":
            if relating_type.is_a() in {"IfcColumnType", "IfcPileType"}:
                data = get_vertical_profile_preview_data(context, relating_type)
            else:
                data = get_horizontal_profile_preview_data(context, relating_type)
        elif tool.Model.get_usage_type(relating_type) == "LAYER2":
            data = get_wall_preview_data(context, relating_type)
        elif tool.Model.get_usage_type(relating_type) == "LAYER3":
            data = get_slab_preview_data(context, relating_type)
        else:
            data = get_generic_product_preview_data(context, relating_type)

        # Update properties so it can be used by the decorator
        props = context.scene.BIMProductPreviewProperties
        props.verts.clear()
        props.edges.clear()
        props.tris.clear()
        if not data:
            return

        for vert in data["verts"]:
            v = props.verts.add()
            v.value_3d = vert
        for edge in data["edges"]:
            e = props.edges.add()
            e.value_2d = edge
        for tri in data["tris"]:
            t = props.tris.add()
            t.value_3d = tri

    def set_offset(self, context: bpy.types.Context, relating_type: ifcopenshell.entity_instance) -> None:
        props = tool.Model.get_model_props()
        direction_sense = props.direction_sense
        if tool.Model.get_usage_type(relating_type) == "LAYER2":
            offset_type = "offset_type_vertical"
            direction = 1 if direction_sense == "POSITIVE" else -1
        elif tool.Model.get_usage_type(relating_type) == "LAYER3":
            offset_type = "offset_type_horizontal"
            direction = 1
        else:
            return

        layers = tool.Model.get_material_layer_parameters(relating_type)
        thickness = layers["thickness"]
        self.offset = 0
        if getattr(props, offset_type) == "CENTER":
            self.offset = (-thickness / 2) * direction
        elif getattr(props, offset_type) in {"INTERIOR", "TOP"}:
            self.offset = -thickness * direction

        self.unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        props.offset = self.offset / self.unit_scale
        tool.Blender.update_viewport()

    def modal(self, context: bpy.types.Context, event: bpy.types.Event) -> Union[set[str], None]:
        PolylineDecorator.update(event, self.tool_state, self.input_ui, self.snapping_points[0])
        tool.Blender.update_viewport()
        if event.type in {"MIDDLEMOUSE", "WHEELUPMOUSE", "WHEELDOWNMOUSE"}:
            return {"PASS_THROUGH"}

    def invoke(self, context: bpy.types.Context, event: bpy.types.Event) -> None:
        PolylineDecorator.install(context)
        tool.Snap.clear_snapping_point()

        self.tool_state.use_default_container = False
        self.tool_state.axis_method = None
        self.tool_state.plane_method = None
        self.tool_state.mode = "Mouse"
        self.visible_objs = tool.Raycast.get_visible_objects(context)
        for obj in self.visible_objs:
            if bbox_2d := tool.Raycast.get_on_screen_2d_bounding_boxes(context, obj):
                self.objs_2d_bbox.append(bbox_2d)
        detected_snaps = tool.Snap.detect_snapping_points(context, event, self.objs_2d_bbox, self.tool_state)
        self.snapping_points = tool.Snap.select_snapping_points(context, event, self.tool_state, detected_snaps)
        tool.Polyline.calculate_distance_and_angle(context, self.input_ui, self.tool_state)

        tool.Blender.update_viewport()
        context.window_manager.modal_handler_add(self)
