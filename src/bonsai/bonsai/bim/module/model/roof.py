# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>, @Andrej730
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

import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.representation
import ifcopenshell.util.unit
import bonsai.core.root
import bonsai.tool as tool
from bonsai.bim.helper import convert_property_group_from_si
from bonsai.bim.module.model.door import bm_sort_out_geom
from bonsai.bim.module.model.data import RoofData, refresh
from bonsai.bim.module.model.decorator import ProfileDecorator

import json
from math import tan, pi, radians
from mathutils import Vector, Matrix
import mathutils.geometry
from bpypolyskel import bpypolyskel
import shapely
from pprint import pprint
from typing import Literal, Union, Any

# reference:
# https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcRoof.htm
# https://ifc43-docs.standards.buildingsmart.org/IFC/RELEASE/IFC4x3/HTML/lexical/IfcRoofType.htm


def bm_mesh_clean_up(bm: bmesh.types.BMesh) -> None:
    # remove internal edges and faces
    # adding missing faces so we could rely on `e.is_boundary` later
    bmesh.ops.contextual_create(bm, geom=bm.edges[:])
    edges_to_dissolve = [e for e in bm.edges if not e.is_boundary]
    bmesh.ops.dissolve_edges(bm, edges=edges_to_dissolve)
    bmesh.ops.delete(bm, geom=bm.faces[:], context="FACES_ONLY")
    bmesh.ops.dissolve_limit(
        bm,
        angle_limit=0.0872665,
        use_dissolve_boundaries=False,
        delimit={"NORMAL"},
        edges=bm.edges[:],
        verts=bm.verts[:],
    )
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)


class GenerateHippedRoof(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.generate_hipped_roof"
    bl_label = "Generate Hipped Roof"
    bl_options = {"REGISTER", "UNDO"}

    roof_generation_methods = (
        ("HEIGHT", "HEIGHT", ""),
        ("ANGLE", "ANGLE", ""),
    )

    mode: bpy.props.EnumProperty(name="Roof Generation Method", items=roof_generation_methods, default="ANGLE")
    height: bpy.props.FloatProperty(
        name="Height", default=1.0, description="Maximum height of the roof to be generated.", subtype="DISTANCE"
    )
    angle: bpy.props.FloatProperty(name="Slope Angle", default=pi / 18, subtype="ANGLE")

    def _execute(self, context):
        obj = bpy.context.active_object
        if not obj:
            self.report({"ERROR"}, "Need to select some object first.")
            return {"CANCELLED"}

        bm = tool.Blender.get_bmesh_for_mesh(obj.data)
        op_status, error_message = is_valid_roof_footprint(bm)
        if error_message:
            self.report(op_status, error_message)
            return {"CANCELLED"}

        generate_hiped_roof_bmesh(bm, self.mode, self.height, self.angle)
        tool.Blender.apply_bmesh(obj.data, bm)
        return {"FINISHED"}


def is_valid_roof_footprint(bm: bmesh.types.BMesh) -> tuple[set[str], str]:
    # should be bmesh to support edit mode
    bm.verts.ensure_lookup_table()
    base_z = bm.verts[0].co.z
    all_verts_same_level = all([tool.Cad.is_x(v.co.z - base_z, 0) for v in bm.verts[1:]])
    if not all_verts_same_level:
        return (
            {"ERROR"},
            "\nAll roof footprint vertices should have same Z-level.\nCurrently Z-level doesn't completely match",
        )
    return ({"FINISHED"}, "")


def generate_hiped_roof_bmesh(
    bm: bmesh.types.BMesh,
    mode: Literal["ANGLE", "HEIGHT"] = "ANGLE",
    height: float = 1.0,
    roof_thickness: float = 0.1,
    angle: float = pi / 18,
    rafter_edge_angle: float = pi / 2,
    mutate_current_bmesh: float = True,
) -> bmesh.types.BMesh:
    """return bmesh with gable roof geometry

    `mutate_current_bmesh` is a flag to indicate whether the input bmesh
    should be mutated or a new bmesh should be created and returned.

    If the object is in EDIT mode then it will be the only way to change it.

    If roof bmesh needed only to supply into decorator then there is no reason to mutate it.
    """

    if not mutate_current_bmesh:
        bm = bm.copy()

    # CLEAN UP
    bm_mesh_clean_up(bm)

    boundary_lines = []

    original_geometry_data = dict()
    angle_layer = bm.edges.layers.float.get("BBIM_gable_roof_angles")
    separate_verts_layer = bm.edges.layers.int.get("BBIM_gable_roof_separate_verts")
    if angle_layer:
        original_geometry_data["edges"] = [
            (set(bm_get_indices(e.verts)), e[angle_layer], e[separate_verts_layer]) for e in bm.edges
        ]
    else:
        original_geometry_data["edges"] = [(set(bm_get_indices(e.verts)), None, None) for e in bm.edges]

    original_geometry_data["verts"] = {v.index: v.co.copy() for v in bm.verts}
    footprint_z = bm.verts[:][0].co.z

    def calculate_hiped_roof():
        for edge in bm.edges:
            boundary_lines.append(shapely.LineString([v.co for v in edge.verts]))

        unioned_boundaries = shapely.union_all(shapely.GeometryCollection(boundary_lines))
        closed_polygons = shapely.polygonize(unioned_boundaries.geoms)

        # find the polygon with the biggest area
        roof_polygon = max(closed_polygons.geoms, key=lambda polygon: polygon.area)

        # add z coordinate if not present
        roof_polygon = shapely.force_3d(roof_polygon)

        # make sure the polygon is counter-clockwise
        if not shapely.is_ccw(roof_polygon):
            roof_polygon = roof_polygon.reverse()

        # Define vertices for the base footprint of the building at height 0.0
        # counterclockwise order
        verts = [Vector(v) for v in roof_polygon.exterior.coords[0:-1]]
        total_exterior_verts = len(verts)
        next_index = total_exterior_verts

        inner_loops = None  # in case when there is no .interiors
        for interior in roof_polygon.interiors:
            if inner_loops is None:
                inner_loops = []
            loop = interior.coords[0:-1]
            total_verts = len(loop)
            verts.extend([Vector(v) for v in loop])
            inner_loops.append((next_index, total_verts))
            next_index += total_verts

        unit_vectors = None  # we have no unit vectors, let them computed by polygonize()
        start_exterior_index = 0

        faces = []
        nonlocal height, angle
        if mode == "HEIGHT":
            height = height
            angle = 0.0
        else:
            angle = tan(angle)
            height = 0.0

        faces = bpypolyskel.polygonize(
            verts, start_exterior_index, total_exterior_verts, inner_loops, height, angle, faces, unit_vectors
        )
        edges = []
        return verts, edges, faces

    verts, edges, faces = calculate_hiped_roof()
    bm.clear()

    new_verts = [bm.verts.new(v) for v in verts]
    new_edges = [bm.edges.new([new_verts[vi] for vi in edge]) for edge in edges]
    new_faces = [bm.faces.new([new_verts[vi] for vi in face]) for face in faces]

    def find_identical_new_vert(co: Vector) -> Union[bmesh.types.BMVert, None]:
        for v in bm.verts:
            if tool.Cad.is_x((co - v.co).length, 0):
                return v

    def find_other_polygon_verts(edge: bmesh.types.BMEdge) -> list[bmesh.types.BMVert]:
        polygon = edge.link_faces[0]
        return [v for v in polygon.verts if v not in edge.verts]

    def change_angle(projected_vert_co: Vector, edge_verts: list[bmesh.types.BMVert], new_angle: float) -> Vector:
        A, B = [v.co for v in edge_verts]
        P = projected_vert_co

        AP = P - A
        AB = B - A
        AB_dir = AB.normalized()
        proj_length = AP.dot(AB_dir)
        C = A + AB_dir * proj_length
        Pp = P * Vector([1, 1, 0]) + Vector([0, 0, C.z])

        Pp = P * Vector([1, 1, 0]) + Vector([0, 0, C.z])
        angle_tan = tan(new_angle)
        dist = (P.z - Pp.z) / angle_tan
        PPnew = C + (Pp - C).normalized() * dist
        Pnew = PPnew * Vector([1, 1, 0]) + Vector([0, 0, P.z])
        return Pnew

    footprint_edges = []
    footprint_verts = set()
    verts_to_change = {}
    verts_to_rip = []
    bottom_chords_to_remove = []

    def is_footprint_vert(v: bmesh.types.BMVert) -> bool:
        return tool.Cad.is_x(v.co.z - footprint_z, 0)

    def is_footprint_edge(edge: bmesh.types.BMEdge) -> bool:
        return all(is_footprint_vert(v) for v in edge.verts)

    # find footprint edges
    for edge in bm.edges:
        if is_footprint_edge(edge):
            footprint_edges.append(edge)
            footprint_verts.update(edge.verts)

    old_verts_remap = {}
    for old_vert in original_geometry_data["verts"]:
        old_vert_co = original_geometry_data["verts"][old_vert]
        old_verts_remap[old_vert] = find_identical_new_vert(old_vert_co)

    # iterate over edges from original geometry
    # if their angle was redefined by user - apply the changes to the related vertices
    # to match the requested angle

    process_later = []
    for old_edge_verts, defined_angle, separate_verts in original_geometry_data["edges"]:
        if not defined_angle:
            continue

        edge_verts_remaped = set(old_verts_remap[old_vert] for old_vert in old_edge_verts)

        identical_edge = None
        for edge in footprint_edges:
            if set(edge.verts) == edge_verts_remaped:
                identical_edge = edge
                break
        assert identical_edge

        if separate_verts:
            verts_to_move = find_other_polygon_verts(identical_edge)
            for v in verts_to_move:
                vert_co = v.co
                new_vert_co = change_angle(vert_co, edge_verts_remaped, defined_angle)
                verts_to_rip.append([v, new_vert_co, identical_edge])
        else:
            process_later.append([identical_edge, edge_verts_remaped, defined_angle])

        if defined_angle >= pi / 2:
            bottom_chords_to_remove.append(identical_edge)

    def separate_vert(
        bm: bmesh.types.BMesh, vert: bmesh.types.BMVert, edge: bmesh.types.BMEdge, new_co: Vector
    ) -> bmesh.types.BMVert:
        face = next(f for f in vert.link_faces if edge in f.edges)
        new_v = bmesh.utils.face_vert_separate(face, vert)
        new_v.co = new_co
        new_edge = bm.edges.new((vert, new_v))

        for cur_edge in face.edges:
            if cur_edge == edge:
                continue
            bmesh.ops.contextual_create(bm, geom=[new_edge, cur_edge])
        return new_v

    # correct angle for verts that require verts separation
    # store separated verts for angle correction later
    related_verts = {}
    for v, new_co, edge in verts_to_rip:
        new_v = separate_vert(bm, v, edge, new_co)
        related_verts.setdefault(v, []).append(new_v)

    # verts angle correction.
    # we're taking into account new verts created after verts separation
    # required for asymmetrical gable roof
    for identical_edge, edge_verts_remaped, defined_angle in process_later:
        verts_to_move = find_other_polygon_verts(identical_edge)
        for v in verts_to_move[:]:
            verts_to_move.extend(related_verts.get(v, []))

        for v in verts_to_move:
            vert_co = verts_to_change.get(v, v.co)
            new_vert_co = change_angle(vert_co, edge_verts_remaped, defined_angle)
            verts_to_change[v] = new_vert_co

    # apply all changes once at the end
    for v in verts_to_change:
        v.co = verts_to_change[v]

    bmesh.ops.delete(bm, geom=bottom_chords_to_remove, context="EDGES")

    # add roof thickness
    extrusion_geom = bm_sort_out_geom(bmesh.ops.extrude_face_region(bm, geom=bm.faces)["geom"])
    extruded_edges = extrusion_geom["edges"]
    extruded_verts = extrusion_geom["verts"]
    rafter_edge_angle = pi / 2 - rafter_edge_angle
    default_offset_dir = Vector([0, 0, 1]) * roof_thickness
    footprint_verts = set()

    if not tool.Cad.is_x(rafter_edge_angle, 0):
        footprint_edges = []
        for edge in extruded_edges:
            if is_footprint_edge(edge):
                footprint_edges.append(edge)
                footprint_verts.update(edge.verts)

        def get_top_vert(v):
            non_footprint_verts = []
            for edge in v.link_edges:
                v1 = edge.other_vert(v)
                if not is_footprint_vert(v1):
                    non_footprint_verts.append(v1)

            if len(non_footprint_verts) == 1:
                return non_footprint_verts[0]

            return min(non_footprint_verts, key=lambda v1: (v1.co - v.co).length)

        top_verts = dict()
        for v in footprint_verts:
            top_verts[v] = get_top_vert(v)

        # TODO: rafter_edge_angle might differ
        # if footprint edges are not connected by 90 degrees
        verts_offsets = dict()
        for edge in footprint_edges:
            v0, v1 = edge.verts
            edge_dir = (v0.co - v1.co).normalized()
            offset_dir = Matrix.Rotation(rafter_edge_angle, 4, edge_dir) @ default_offset_dir
            for v in edge.verts:
                previous_offset = verts_offsets.get(v, None)
                if previous_offset:
                    previous_offset.xy += offset_dir.xy
                else:
                    verts_offsets[v] = offset_dir

        for v in verts_offsets:
            vert_offset = verts_offsets[v]
            top = top_verts[v].co
            bot = v.co + default_offset_dir
            base = v.co
            offsetted = v.co + vert_offset
            # all this math is needed to maintain the same roof thickness
            # for different rafter edge angles
            v.co = mathutils.geometry.intersect_line_line(bot, top, base, offsetted)[0]

    verts = [v for v in extruded_verts if v not in footprint_verts]
    bmesh.ops.translate(bm, vec=default_offset_dir, verts=verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return bm


def bm_get_indices(sequence) -> list[int]:
    return [i.index for i in sequence]


def update_roof_modifier_ifc_data(context: bpy.types.Context) -> None:
    """should be called after new geometry settled
    since it's going to update ifc representation
    """
    obj = context.active_object
    props = obj.BIMRoofProperties
    element = tool.Ifc.get_entity(obj)

    def roof_is_gabled() -> bool:
        pset_data = tool.Model.get_modeling_bbim_pset_data(obj, "BBIM_Roof")
        path_data = pset_data["data_dict"]["path_data"]
        angle_layer = path_data.get("gable_roof_angles", None)
        if not angle_layer:
            return False
        for edge_angle in angle_layer:
            if tool.Cad.is_x(edge_angle - pi / 2, 0):
                return True
        return False

    # type attributes
    if props.roof_type == "HIP/GABLE ROOF":
        element.PredefinedType = "GABLE_ROOF" if roof_is_gabled() else "HIP_ROOF"

    # occurrences attributes
    # occurrences = tool.Ifc.get_all_element_occurrences(element)

    tool.Model.add_body_representation(obj)


def update_bbim_roof_pset(element: ifcopenshell.entity_instance, roof_data: dict[str, Any]) -> None:
    pset = tool.Pset.get_element_pset(element, "BBIM_Roof")
    if not pset:
        pset = ifcopenshell.api.run("pset.add_pset", tool.Ifc.get(), product=element, name="BBIM_Roof")
    roof_data = tool.Ifc.get().createIfcText(json.dumps(roof_data, default=list))
    ifcopenshell.api.run("pset.edit_pset", tool.Ifc.get(), pset=pset, properties={"Data": roof_data})


def update_roof_modifier_bmesh(obj: bpy.types.Object) -> None:
    """before using should make sure that Data contains up-to-date information.
    If BBIM Pset just changed should call refresh() before updating bmesh
    """
    props = obj.BIMRoofProperties
    assert isinstance(obj.data, bpy.types.Mesh)

    # NOTE: using Data since bmesh update will hapen very often
    if not RoofData.is_loaded:
        RoofData.load()
    path_data = RoofData.data["pset_data"]["data_dict"]["path_data"]
    angle_layer_data = path_data.get("gable_roof_angles", None)
    separate_verts_data = path_data.get("gable_roof_separate_verts", None)

    si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
    # need to make sure we support edit mode
    # since users will probably be in edit mode when they'll be changing roof path
    bm = tool.Blender.get_bmesh_for_mesh(obj.data, clean=True)
    angle_layer = bm.edges.layers.float.new("BBIM_gable_roof_angles")
    separate_verts_layer = bm.edges.layers.int.new("BBIM_gable_roof_separate_verts")

    # generating roof path
    new_verts = [bm.verts.new(Vector(v) * si_conversion) for v in path_data["verts"]]
    new_edges = []
    for i in range(len(path_data["edges"])):
        e = path_data["edges"][i]
        edge = bm.edges.new((new_verts[e[0]], new_verts[e[1]]))
        edge[angle_layer] = angle_layer_data[i] if angle_layer_data else 0
        edge[separate_verts_layer] = separate_verts_data[i] if separate_verts_data else 0
        new_edges.append(edge)

    if props.is_editing_path:
        tool.Blender.apply_bmesh(obj.data, bm)
        return

    generate_hiped_roof_bmesh(
        bm,
        props.generation_method,
        props.height,
        props.roof_thickness,
        props.angle,
        props.rafter_edge_angle,
        mutate_current_bmesh=True,
    )
    tool.Blender.apply_bmesh(obj.data, bm)


def get_path_data(obj: bpy.types.Object) -> Union[dict[str, Any], None]:
    """get path data for current mesh, path data is cleaned up"""
    si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

    if obj.mode == "EDIT":
        # otherwise mesh may not contain all changes
        # added in edit mode
        obj.update_from_editmode()

    bm = tool.Blender.get_bmesh_for_mesh(obj.data)
    bm_mesh_clean_up(bm)

    angle_layer = bm.edges.layers.float.get("BBIM_gable_roof_angles")
    separate_verts_layer = bm.edges.layers.int.get("BBIM_gable_roof_separate_verts")

    path_data = dict()
    path_data["edges"] = [bm_get_indices(e.verts) for e in bm.edges]
    path_data["verts"] = [v.co / si_conversion for v in bm.verts]
    if angle_layer:
        path_data["gable_roof_angles"] = [e[angle_layer] for e in bm.edges]
    if separate_verts_layer:
        path_data["gable_roof_separate_verts"] = [e[separate_verts_layer] for e in bm.edges]

    if not path_data["edges"] or not path_data["verts"]:
        return None
    return path_data


class BIM_OT_add_roof(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "mesh.add_roof"
    bl_label = "Roof"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return tool.Ifc.get() and context.mode == "OBJECT"

    def _execute(self, context):
        ifc_file = tool.Ifc.get()
        if not ifc_file:
            self.report({"ERROR"}, "You need to start IFC project first to create a roof.")
            return {"CANCELLED"}

        if context.active_object is not None:
            spawn_location = context.active_object.location.copy()
            context.active_object.select_set(False)
        else:
            spawn_location = bpy.context.scene.cursor.location.copy()

        mesh = bpy.data.meshes.new("IfcRoof")
        obj = bpy.data.objects.new("IfcRoof", mesh)
        obj.location = spawn_location

        body_context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
        bonsai.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class="IfcRoof",
            should_add_representation=True,
            context=body_context,
        )
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = None
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.bim.add_roof()
        return {"FINISHED"}


# UI operators
class AddRoof(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.add_roof"
    bl_label = "Add Roof"
    bl_description = "Add Bonsai parametric roof to the active IFC element"
    bl_options = {"REGISTER", "UNDO"}

    def _execute(self, context):
        obj = context.active_object
        assert obj
        element = tool.Ifc.get_entity(obj)
        props = obj.BIMRoofProperties
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

        # rejecting original roof shape to be safe
        # taking into account only it's bounding box dimensions
        if obj.dimensions.x == 0 or obj.dimensions.y == 0:
            min_x, min_y = -5, -5
            max_x, max_y = 5, 5
            min_z = 0
        else:
            bbox = tool.Blender.get_object_bounding_box(obj)
            min_x = bbox["min_x"]
            min_y = bbox["min_y"]
            max_x = bbox["max_x"]
            max_y = bbox["max_y"]
            min_z = bbox["min_z"]

        roof_data = props.get_general_kwargs(convert_to_project_units=True)
        path_data = {
            "edges": [[0, 1], [1, 2], [2, 3], [3, 0]],
            "verts": [
                Vector([min_x, min_y, min_z]) / si_conversion,
                Vector([min_x, max_y, min_z]) / si_conversion,
                Vector([max_x, max_y, min_z]) / si_conversion,
                Vector([max_x, min_y, min_z]) / si_conversion,
            ],
        }
        roof_data["path_data"] = path_data

        update_bbim_roof_pset(element, roof_data)
        refresh()

        if obj.type == "EMPTY":
            obj = tool.Geometry.recreate_object_with_data(obj, data=bpy.data.meshes.new("temp"), is_global=True)
            tool.Blender.set_active_object(obj)

        update_roof_modifier_bmesh(obj)
        update_roof_modifier_ifc_data(context)
        tool.Model.add_body_representation(obj)


class EnableEditingRoof(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_roof"
    bl_label = "Enable Editing Roof"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        props = obj.BIMRoofProperties
        data = tool.Model.get_modeling_bbim_pset_data(obj, "BBIM_Roof")["data_dict"]
        # required since we could load pset from .ifc and BIMRoofProperties won't be set
        props.set_props_kwargs_from_ifc_data(data)
        props.is_editing = True
        return {"FINISHED"}


class CancelEditingRoof(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.cancel_editing_roof"
    bl_label = "Cancel Editing Roof"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        assert obj
        data = tool.Model.get_modeling_bbim_pset_data(obj, "BBIM_Roof")["data_dict"]
        props = obj.BIMRoofProperties

        # restore previous settings since editing was canceled
        props.set_props_kwargs_from_ifc_data(data)
        update_roof_modifier_bmesh(obj)

        props.is_editing = False
        return {"FINISHED"}


class FinishEditingRoof(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.finish_editing_roof"
    bl_label = "Finish Editing Roof"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        props = obj.BIMRoofProperties

        pset_data = tool.Model.get_modeling_bbim_pset_data(obj, "BBIM_Roof")
        path_data = pset_data["data_dict"]["path_data"]

        roof_data = props.get_general_kwargs(convert_to_project_units=True)
        roof_data["path_data"] = path_data
        props.is_editing = False

        update_bbim_roof_pset(element, roof_data)
        update_roof_modifier_ifc_data(context)
        return {"FINISHED"}


class EnableEditingRoofPath(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.enable_editing_roof_path"
    bl_label = "Edit Roof"
    bl_description = "Enable Editing Roof Path"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        assert obj
        [o.select_set(False) for o in context.selected_objects if o != obj]
        props = obj.BIMRoofProperties
        data = tool.Model.get_modeling_bbim_pset_data(obj, "BBIM_Roof")["data_dict"]
        # required since we could load pset from .ifc and BIMRoofProperties won't be set
        props.set_props_kwargs_from_ifc_data(data)

        props.is_editing_path = True
        update_roof_modifier_bmesh(obj)

        if bpy.context.active_object.mode != "EDIT":
            bpy.ops.object.mode_set(mode="EDIT")
        tool.Blender.set_viewport_tool("bim.cad_tool")

        def mark_preview_edges(bm, bew_verts, new_edges, new_faces):
            preview_layer = bm.edges.layers.int["BBIM_preview"]
            # can't create layer in callback because it kill all the bm edge references
            for edge in new_edges:
                edge[preview_layer] = 1

        def get_custom_bmesh():
            # copying to make sure not to mutate the edit mode bmesh
            bm = tool.Blender.get_bmesh_for_mesh(obj.data)
            main_bm = bm.copy()
            op_status, error_message = is_valid_roof_footprint(main_bm)
            if error_message:
                print("Error: %s" % error_message)
                return main_bm

            main_bm.edges.layers.int.new("BBIM_preview")

            second_bm = generate_hiped_roof_bmesh(
                bm,
                props.generation_method,
                props.height,
                props.roof_thickness,
                props.angle,
                props.rafter_edge_angle,
                mutate_current_bmesh=False,
            )
            bmesh.ops.translate(second_bm, verts=second_bm.verts, vec=Vector((0, 0, 1)))

            tool.Blender.bmesh_join(main_bm, second_bm, callback=mark_preview_edges)
            return main_bm

        ProfileDecorator.install(
            context,
            get_custom_bmesh,
            draw_faces=True,
            exit_edit_mode_callback=lambda: cancel_editing_roof_path(context),
        )
        return {"FINISHED"}


def cancel_editing_roof_path(context: bpy.types.Context) -> set[str]:
    obj = context.active_object
    assert obj
    props = obj.BIMRoofProperties

    ProfileDecorator.uninstall()
    props.is_editing_path = False

    update_roof_modifier_bmesh(obj)
    if obj.mode == "EDIT":
        bpy.ops.object.mode_set(mode="OBJECT")
    return {"FINISHED"}


class CancelEditingRoofPath(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.cancel_editing_roof_path"
    bl_label = "Cancel Editing Roof Path"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        return cancel_editing_roof_path(context)


class FinishEditingRoofPath(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.finish_editing_roof_path"
    bl_label = "Finish Editing Roof Path"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        props = obj.BIMRoofProperties

        bm = tool.Blender.get_bmesh_for_mesh(obj.data)
        op_status, error_message = is_valid_roof_footprint(bm)
        if error_message:
            self.report(op_status, error_message)
            return {"CANCELLED"}

        roof_data = props.get_general_kwargs(convert_to_project_units=True)
        path_data = get_path_data(obj)
        roof_data["path_data"] = path_data
        ProfileDecorator.uninstall()
        props.is_editing_path = False

        update_bbim_roof_pset(element, roof_data)
        refresh()  # RoofData has to be updated before run update_roof_modifier_bmesh
        update_roof_modifier_bmesh(obj)

        update_roof_modifier_ifc_data(context)
        if bpy.context.active_object.mode == "EDIT":
            bpy.ops.object.mode_set(mode="OBJECT")
        update_roof_modifier_ifc_data(context)
        return {"FINISHED"}


class RemoveRoof(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.remove_roof"
    bl_label = "Remove Roof"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        obj.BIMRoofProperties.is_editing = False

        pset = tool.Pset.get_element_pset(element, "BBIM_Roof")
        ifcopenshell.api.run("pset.remove_pset", tool.Ifc.get(), product=element, pset=pset)
        return {"FINISHED"}


class SetGableRoofEdgeAngle(bpy.types.Operator):
    bl_idname = "bim.set_gable_roof_edge_angle"
    bl_label = "Set Gable Roof Edge Angle"
    bl_options = {"REGISTER", "UNDO"}
    angle: bpy.props.FloatProperty(name="Angle", default=90)
    separate_verts: bpy.props.BoolProperty(name="Separate Verts", default=True)

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == "MESH" and context.mode == "EDIT_MESH"

    def draw(self, context):
        layout = self.layout
        for prop in self.__class__.__annotations__.keys():
            layout.prop(self, prop)

    def execute(self, context):
        # tried to avoid bmesh with foreach_get and foreach_set
        # but in EDIT mode it's only possible to change attributes by working with bmesh

        me = context.active_object.data
        bm = tool.Blender.get_bmesh_for_mesh(me)

        # check if attribute exists or create one
        if "BBIM_gable_roof_angles" not in me.attributes:
            me.attributes.new("BBIM_gable_roof_angles", type="FLOAT", domain="EDGE")

        if "BBIM_gable_roof_separate_verts" not in me.attributes:
            me.attributes.new("BBIM_gable_roof_separate_verts", type="INT", domain="EDGE")

        angles_layer = bm.edges.layers.float["BBIM_gable_roof_angles"]
        separate_verts_layer = bm.edges.layers.int["BBIM_gable_roof_separate_verts"]

        for e in bm.edges:
            if not e.select:
                continue
            e[angles_layer] = self.angle
            e[separate_verts_layer] = self.separate_verts

        tool.Blender.apply_bmesh(me, bm)
        return {"FINISHED"}
