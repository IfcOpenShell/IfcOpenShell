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
import ifcopenshell.api.pset
import ifcopenshell.util.representation
import ifcopenshell.util.unit
import bonsai.core.root
import bonsai.tool as tool
from bonsai.bim.module.model.data import RoofData, refresh
from bonsai.bim.module.model.decorator import ProfileDecorator

import json
from math import cos, tan, pi, radians
from mathutils import Vector, Matrix, Quaternion
import mathutils.geometry
from bpypolyskel import bpypolyskel
import shapely
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

        generate_hipped_roof_bmesh(bm, self.mode, self.height, self.angle)
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


def generate_hipped_roof_bmesh(
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

    bm_mesh_clean_up(bm)

    rafter_edge_angle = pi / 2 - rafter_edge_angle  # It's easier to work with this angle.
    angled_edges = []
    angle_layer = bm.edges.layers.float.get("BBIM_gable_roof_angles")
    if angle_layer:
        angled_edges = [
            (set([v.co.copy().freeze() for v in e.verts]), e[angle_layer]) for e in bm.edges if e[angle_layer]
        ]

    footprint_z = bm.verts[:][0].co.z

    def calculate_hipped_roof():
        boundary_lines = []
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
            tan_angle = 0.0
        else:
            tan_angle = tan(angle)
            height = 0.0

        # I think bpypolyskel upstream has a bug which can cause sloped ridges
        # where it is not necessary to have sloped ridges specifically for
        # dormers. This seems to work, but I'm not confident because apparently
        # you need a PhD to understand this. See bug #5319.
        if not hasattr(bpypolyskel._SLAV, "unpatched_handle_dormer_event"):

            def patched_handle_dormer_event(self, event):
                result = self.unpatched_handle_dormer_event(event)
                if result[0]:
                    result[0][1] = bpypolyskel.Subtree(result[0][1].source, result[0][0].height, result[0][1].sinks)
                return result

            bpypolyskel._SLAV.unpatched_handle_dormer_event = bpypolyskel._SLAV.handle_dormer_event
            bpypolyskel._SLAV.handle_dormer_event = patched_handle_dormer_event

        faces = bpypolyskel.polygonize(
            verts, start_exterior_index, total_exterior_verts, inner_loops, height, tan_angle, faces, unit_vectors
        )

        edges = []
        return verts, edges, faces

    verts, edges, faces = calculate_hipped_roof()
    bm.clear()

    new_verts = [bm.verts.new(v) for v in verts]
    new_edges = [bm.edges.new([new_verts[vi] for vi in edge]) for edge in edges]
    new_faces = [bm.faces.new([new_verts[vi] for vi in face]) for face in faces]

    if mode == "HEIGHT":  # Calculate the angle we ended up with.
        new_faces[0].normal_update()
        angle = new_faces[0].normal.angle(Vector((0, 0, 1)))

    # bpypolyskel performs a straight skeleton with equal weights. Ideally, we
    # need support for weighted straight skeletons (CGAL has this function) to
    # calculate skeletons of varying angles. Doing anything else, such as
    # creating new vertices, splitting edges, or sliding vertices is extremely
    # error prone and only works in simple scenarios.

    # In the meantime, we can support the simplest, but luckily also most
    # common scenario of a gable roof, or hipped roof where the varied angle
    # only occurs on a triangle face.

    def is_footprint_edge(edge: bmesh.types.BMEdge) -> bool:
        return all(tool.Cad.is_x(v.co.z - footprint_z, 0) for v in edge.verts)

    footprint_edges = set()
    gable_edges = set()
    edges_to_delete = set()
    face_angles = {}

    # Post process skeleton to handle gables and custom angles.
    for edge in bm.edges:
        if not is_footprint_edge(edge):
            continue
        footprint_edges.add(edge)
        if len(edge.link_faces) != 1 or len(edge.link_faces[0].verts) != 3:
            continue  # Too complicated for us to figure out without a weighted skeleton
        face_verts = edge.link_faces[0].verts
        verts = set([v.co.copy().freeze() for v in edge.verts])
        for angled_edge, edge_angle in angled_edges:
            if angled_edge == verts:
                face_angles[edge.link_faces[0]] = edge_angle
                ridge_vert = [v for v in face_verts if v.co.copy().freeze() not in verts][0]
                if len(ridge_vert.link_edges) == 3:
                    ridge_edge = [e for e in ridge_vert.link_edges if e not in edge.link_faces[0].edges][0]
                    other_ridge_vert = ridge_edge.other_vert(ridge_vert)
                else:
                    # We cannot actually get this correct without a weighted
                    # skeleton, but for now let's assume we duplicate the ridge
                    # vert and slide the vertex towards the midpoint of the
                    # footprint edge.
                    edge_midpoint = edge.verts[0].co.lerp(edge.verts[1].co, 0.5)
                    edge_midpoint.z = ridge_vert.co.z
                    poke = bmesh.ops.poke(bm, faces=[edge.link_faces[0]])
                    other_ridge_vert = poke["verts"][0]
                    other_ridge_vert.co = ridge_vert.co + (edge_midpoint - ridge_vert.co).normalized() * 0.01
                    ridge_vert, other_ridge_vert = other_ridge_vert, ridge_vert

                face_center = (face_verts[0].co + face_verts[1].co + face_verts[2].co) / 3
                x_axis = (edge.verts[1].co - edge.verts[0].co).normalized()
                z_axis = Vector((0, 0, -1))
                y_axis = z_axis.cross(x_axis)
                positive = edge.verts[0].co + (y_axis * 0.01)
                negative = edge.verts[0].co - (y_axis * 0.01)
                if (face_center - positive).length < (face_center - negative).length:
                    y_axis = -y_axis
                    x_axis = y_axis.cross(z_axis)  # Recalculate X axis to make rotation sign consistent
                rotation_quaternion = Quaternion(x_axis, edge_angle)
                plane_no = rotation_quaternion @ z_axis

                if intersect := tool.Cad.intersect_edge_plane(
                    other_ridge_vert.co, ridge_vert.co, edge.verts[0].co, plane_no
                ):
                    edge_percent = tool.Cad.edge_percent(intersect, (other_ridge_vert.co, ridge_vert.co))
                    if edge_percent <= 0:
                        ridge_vert.co = other_ridge_vert.co
                    else:
                        ridge_vert.co = intersect

                if tool.Cad.is_x(edge_angle, pi / 2, tolerance=radians(1)):
                    footprint_edges.remove(edge)
                    edges_to_delete.add(edge)
                    gable_edges.update(
                        [e for e in ridge_vert.link_edges if e.other_vert(ridge_vert) != other_ridge_vert]
                    )
                break

    bmesh.ops.delete(bm, geom=list(edges_to_delete), context="EDGES")

    # Determine cutting planes for rafter_edge_angle
    # The skeleton is always extruded in the -Z. A cutting plane is applied at
    # the footprint or gable edge if a rafter_edge_angle is specified.
    cutting_planes = {}
    bm.faces.ensure_lookup_table()

    if not tool.Cad.is_x(rafter_edge_angle, 0, tolerance=radians(1)):
        for e in footprint_edges:
            face = e.link_faces[0]
            planes = []
            verts = [v.co for v in face.verts]
            face_center = sum(verts[1:], start=verts[0].copy()) / len(verts)
            v1, v2 = [v.co.copy() for v in e.verts]
            if not tool.Cad.is_x(v1.z, footprint_z):
                v1, v2 = v2, v1
            x_axis = (v2 - v1).normalized()
            z_axis = Vector((0, 0, -1))
            y_axis = z_axis.cross(x_axis)
            positive = v1 + (y_axis * 0.01)
            negative = v1 - (y_axis * 0.01)
            plane_no = y_axis
            if (face_center - positive).length < (face_center - negative).length:
                plane_no = -y_axis
                x_axis = plane_no.cross(z_axis)  # Recalculate X axis to make rotation sign consistent
            rotation_quaternion = Quaternion(x_axis, rafter_edge_angle)
            plane_no = rotation_quaternion @ plane_no
            planes.append((v1, plane_no))
            cutting_planes[face] = planes

        # Gable edges are special - they are not cut at the rafter_edge_angle.
        # We copy the neighbouring cutting planes to make sure they mitre
        # correctly.
        for e in gable_edges:
            face = e.link_faces[0]
            planes = []
            neighbouring_faces = set()
            neighbouring_faces.update(e.verts[0].link_faces)
            neighbouring_faces.update(e.verts[1].link_faces)
            for f in neighbouring_faces:
                planes.extend(cutting_planes.get(f, []))
            cutting_planes[face] = planes

    # Extrude skeleton using roof thickness
    for top_face in [f for f in bm.faces]:
        face = top_face.copy()
        face.tag = True  # Tags keep track of which geometry is part of our current skeleton fragment

        if face.normal.z > 0:
            face.normal_flip()

        # This means that different fragments of the roof may not exactly join together.
        # It's technically correct, but may look weird if the architect doesn't know what they're doing.
        face_angle = face_angles.get(top_face, angle)
        # Alternatively maybe we can offer a "distort" mode which doesn't preserve thickness at custom angles:
        # face_angle = angle
        extrusion_height = roof_thickness / cos(face_angle)
        extrusion_vector = Vector((0, 0, -1)) * extrusion_height
        extrusion = tool.Model.bm_sort_out_geom(bmesh.ops.extrude_face_region(bm, geom=[face])["geom"])
        bmesh.ops.translate(bm, vec=extrusion_vector, verts=extrusion["verts"])

        for plane_co, plane_no in cutting_planes.get(top_face, []):
            geom = set()
            for f in bm.faces:
                if f.tag:
                    geom.add(f)
                    for e in f.edges:
                        geom.add(e)
                    for v in f.verts:
                        geom.add(v)

            result = bmesh.ops.bisect_plane(
                bm, geom=list(geom), plane_co=plane_co, plane_no=plane_no, clear_outer=True, clear_inner=False
            )
            for g in result["geom"]:
                if isinstance(g, bmesh.types.BMFace):
                    g.tag = True
            bm.faces.ensure_lookup_table()
            result = bmesh.ops.triangle_fill(
                bm, use_dissolve=True, edges=[g for g in result["geom_cut"] if isinstance(g, bmesh.types.BMEdge)]
            )
            for g in result["geom"]:
                if isinstance(g, bmesh.types.BMFace):
                    g.tag = True
            verts = set()
            [verts.update(f.verts) for f in bm.faces if f.tag]
            bmesh.ops.remove_doubles(bm, verts=list(verts), dist=1e-4)

        for f in bm.faces:
            f.tag = False

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])

    # Merge fragments and remove internal faces.
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    faces_to_delete = set()
    for face in [f for f in bm.faces]:
        is_internal = True
        for e in face.edges:
            if len(e.link_faces) < 3:
                is_internal = False
        if is_internal:
            faces_to_delete.add(face)
    bmesh.ops.delete(bm, geom=list(faces_to_delete), context="FACES")
    return bm


def bm_get_indices(sequence) -> list[int]:
    return [i.index for i in sequence]


def update_roof_modifier_ifc_data(context: bpy.types.Context) -> None:
    """should be called after new geometry settled
    since it's going to update ifc representation
    """
    obj = context.active_object
    assert obj
    props = tool.Model.get_roof_props(obj)
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
    ifc_class = element.is_a()
    if ifc_class in ("IfcRoof", "IfcRoofType"):
        if props.roof_type == "HIP/GABLE ROOF":
            element.PredefinedType = "GABLE_ROOF" if roof_is_gabled() else "HIP_ROOF"
    elif ifc_class in ("IfcSlab", "IfcSlabType"):
        element.PredefinedType = "ROOF"
    elif ifc_class in ("IfcCoveringType", "IfcCoveringType"):
        element.PredefinedType = "ROOFING"

    tool.Model.add_body_representation(obj)


def update_bbim_roof_pset(element: ifcopenshell.entity_instance, roof_data: dict[str, Any]) -> None:
    pset = tool.Pset.get_element_pset(element, "BBIM_Roof")
    if not pset:
        pset = ifcopenshell.api.pset.add_pset(tool.Ifc.get(), product=element, name="BBIM_Roof")
    roof_data = tool.Ifc.get().createIfcText(json.dumps(roof_data, default=list))
    ifcopenshell.api.pset.edit_pset(tool.Ifc.get(), pset=pset, properties={"Data": roof_data})


def update_roof_modifier_bmesh(obj: bpy.types.Object) -> None:
    """before using should make sure that Data contains up-to-date information.
    If BBIM Pset just changed should call refresh() before updating bmesh
    """
    props = tool.Model.get_roof_props(obj)
    assert isinstance(obj.data, bpy.types.Mesh)

    # NOTE: using Data since bmesh update will hapen very often
    if not RoofData.is_loaded:
        RoofData.load()
    path_data = RoofData.data["path_data"]
    angle_layer_data = path_data.get("gable_roof_angles", None)

    si_conversion = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
    # need to make sure we support edit mode
    # since users will probably be in edit mode when they'll be changing roof path
    bm = tool.Blender.get_bmesh_for_mesh(obj.data, clean=True)
    angle_layer = bm.edges.layers.float.new("BBIM_gable_roof_angles")

    # generating roof path
    new_verts = [bm.verts.new(Vector(v) * si_conversion) for v in path_data["verts"]]
    for i in range(len(path_data["edges"])):
        e = path_data["edges"][i]
        edge = bm.edges.new((new_verts[e[0]], new_verts[e[1]]))
        edge[angle_layer] = angle_layer_data[i] if angle_layer_data else 0

    if props.is_editing_path:
        tool.Blender.apply_bmesh(obj.data, bm)
        return

    generate_hipped_roof_bmesh(
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

    path_data = dict()
    path_data["edges"] = [bm_get_indices(e.verts) for e in bm.edges]
    path_data["verts"] = [v.co / si_conversion for v in bm.verts]
    if angle_layer:
        path_data["gable_roof_angles"] = [e[angle_layer] for e in bm.edges]

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
        tool.Blender.select_object(obj)
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
        props = tool.Model.get_roof_props(obj)
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
        assert obj
        props = tool.Model.get_roof_props(obj)
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
        props = tool.Model.get_roof_props(obj)

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
        props = tool.Model.get_roof_props(obj)

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
        props = tool.Model.get_roof_props(obj)
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

            second_bm = generate_hipped_roof_bmesh(
                bm,
                props.generation_method,
                props.height,
                props.roof_thickness,
                props.angle,
                props.rafter_edge_angle,
                mutate_current_bmesh=False,
            )

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
    props = tool.Model.get_roof_props(obj)

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


class CopyRoofParameters(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.copy_roof_parameters"
    bl_label = "Copy Roof Parameters from Active to Selected"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.active_object and len(context.selected_objects) > 1

    def _execute(self, context):
        source_obj = context.active_object
        assert source_obj
        source_props = tool.Model.get_roof_props(source_obj)
        data = source_props.get_general_kwargs(convert_to_project_units=True)

        for target_obj in context.selected_objects:
            if target_obj == source_obj:
                continue
            context.view_layer.objects.active = target_obj
            RoofData.load()
            if not "path_data" in RoofData.data:
                continue
            data["path_data"] = RoofData.data["path_data"]
            target_element = tool.Ifc.get_entity(target_obj)
            target_props = tool.Model.get_roof_props(target_obj)

            target_props.set_props_kwargs_from_ifc_data(data)
            update_bbim_roof_pset(target_element, data)
            refresh()
            update_roof_modifier_bmesh(target_obj)
            update_roof_modifier_ifc_data(context)

        context.view_layer.objects.active = source_obj
        return {"FINISHED"}


class FinishEditingRoofPath(bpy.types.Operator, tool.Ifc.Operator):
    bl_idname = "bim.finish_editing_roof_path"
    bl_label = "Finish Editing Roof Path"
    bl_options = {"REGISTER"}

    def _execute(self, context):
        obj = context.active_object
        element = tool.Ifc.get_entity(obj)
        props = tool.Model.get_roof_props(obj)

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
        assert obj
        element = tool.Ifc.get_entity(obj)
        props = tool.Model.get_roof_props(obj)
        props.is_editing = False

        assert element
        pset = tool.Pset.get_element_pset(element, "BBIM_Roof")
        ifcopenshell.api.pset.remove_pset(tool.Ifc.get(), product=element, pset=pset)
        return {"FINISHED"}


class SetGableRoofEdgeAngle(bpy.types.Operator):
    bl_idname = "bim.set_gable_roof_edge_angle"
    bl_label = "Set Gable Roof Edge Angle"
    bl_options = {"REGISTER", "UNDO"}
    angle: bpy.props.FloatProperty(name="Angle", default=90)

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

        angles_layer = bm.edges.layers.float["BBIM_gable_roof_angles"]

        for e in bm.edges:
            if not e.select:
                continue
            e[angles_layer] = self.angle

        tool.Blender.apply_bmesh(me, bm)
        return {"FINISHED"}
