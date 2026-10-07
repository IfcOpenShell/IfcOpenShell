# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026 Ryan Schultz
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

# This file was generated with the assistance of an AI coding tool.

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Union

import bpy
import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.drawing
import ifcopenshell.api.geometry
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.util.element
import ifcopenshell.util.representation
import ifcopenshell.util.unit
import numpy as np
from ifcopenshell.util.shape_builder import ShapeBuilder
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import bonsai.core.geometry
import bonsai.core.root
import bonsai.core.tool
import bonsai.tool as tool

if TYPE_CHECKING:
    from bonsai.bim.module.terrain.prop import BIMTerrainProperties


# A polyline as an (N, 3) array of points, and whether it closes on itself.
Polyline = tuple[np.ndarray, bool]

CONTOUR_PSET = "BBIM_Contours"
MAX_CONTOUR_LEVELS = 2000
# Faces steeper than this (|normal.z| below it) are treated as walls, not terrain.
TOP_FACE_NORMAL_THRESHOLD = 0.1


class Terrain(bonsai.core.tool.Terrain):
    @classmethod
    def get_terrain_props(cls) -> BIMTerrainProperties:
        return bpy.context.scene.BIMTerrainProperties

    @classmethod
    def is_terrain(cls, element: ifcopenshell.entity_instance) -> bool:
        return element.is_a("IfcGeographicElement") or element.is_a("IfcSite")

    @classmethod
    def get_contour_settings(cls, element: ifcopenshell.entity_instance) -> Union[tuple[float, int], None]:
        """Return (interval in SI metres, index interval) from the terrain's BBIM_Contours pset."""
        pset = ifcopenshell.util.element.get_pset(element, CONTOUR_PSET)
        if not pset or not pset.get("Interval"):
            return None
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        return pset["Interval"] * unit_scale, int(pset.get("IndexInterval") or 0)

    @classmethod
    def set_contour_settings(cls, element: ifcopenshell.entity_instance, interval: float, index_interval: int) -> None:
        ifc_file = tool.Ifc.get()
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        pset = tool.Pset.get_element_pset(element, CONTOUR_PSET)
        if not pset:
            pset = ifcopenshell.api.pset.add_pset(ifc_file, product=element, name=CONTOUR_PSET)
        ifcopenshell.api.pset.edit_pset(
            ifc_file,
            pset=pset,
            properties={"Interval": interval / unit_scale, "IndexInterval": index_interval},
        )

    @classmethod
    def remove_contour_settings(cls, element: ifcopenshell.entity_instance) -> None:
        if pset := tool.Pset.get_element_pset(element, CONTOUR_PSET):
            ifcopenshell.api.pset.remove_pset(tool.Ifc.get(), product=element, pset=pset)

    @classmethod
    def get_contours(cls, element: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        contours = []
        for rel in getattr(element, "ReferencedBy", []) or []:
            if not rel.is_a("IfcRelAssignsToProduct"):
                continue
            for related_object in rel.RelatedObjects:
                if cls.is_contour(related_object):
                    contours.append(related_object)
        return contours

    @classmethod
    def is_contour(cls, element: ifcopenshell.entity_instance) -> bool:
        return element.is_a("IfcAnnotation") and ifcopenshell.util.element.get_predefined_type(element) == "CONTOURLINE"

    @classmethod
    def remove_contour(cls, contour: ifcopenshell.entity_instance) -> None:
        if obj := tool.Ifc.get_object(contour):
            tool.Geometry.delete_ifc_object(obj)
        else:
            ifcopenshell.api.root.remove_product(tool.Ifc.get(), product=contour)

    @classmethod
    def get_elevation_offset(cls) -> float:
        """SI offset to add to a Blender Z to get the project (IFC) Z."""
        if not tool.Georeference.has_blender_offset():
            return 0.0
        props = tool.Georeference.get_georeference_props()
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        return float(props.blender_offset_z) * unit_scale

    @classmethod
    def get_contour_levels(
        cls, element: ifcopenshell.entity_instance, interval: float
    ) -> list[tuple[int, float, list[Polyline]]]:
        """Slice the terrain's top surface every ``interval`` (SI) metres of project elevation.

        :return: (level index, Blender world Z, polylines in Blender world coordinates) per
            elevation that has at least one contour. The project elevation is ``index * interval``.
        """
        obj = tool.Ifc.get_object(element)
        if not isinstance(obj, bpy.types.Object) or not isinstance(obj.data, bpy.types.Mesh):
            return []
        verts, tris = cls.get_top_surface_triangles(obj)
        if not len(tris):
            return []

        offset = cls.get_elevation_offset()
        used_z = verts[np.unique(tris), 2]
        first = math.ceil((used_z.min() + offset) / interval)
        last = math.floor((used_z.max() + offset) / interval)
        if last - first + 1 > MAX_CONTOUR_LEVELS:
            raise ValueError(
                f"An interval of {interval}m would create {last - first + 1} contours. "
                f"Use a larger interval (at most {MAX_CONTOUR_LEVELS} contours)."
            )

        levels = []
        for i in range(first, last + 1):
            z = i * interval - offset
            if polylines := cls.slice_triangles(verts, tris, z):
                levels.append((i, z, polylines))
        return levels

    @classmethod
    def get_top_surface_triangles(cls, obj: bpy.types.Object) -> tuple[np.ndarray, np.ndarray]:
        """World-space vertices and the triangles of the surface visible from directly above.

        Face normals cannot tell the top of a solid terrain from its bottom (imported meshes often
        have flipped winding), so a triangle is "top" when it is not near-vertical and a ray cast
        straight up from it hits nothing else in the mesh.

        The test is per triangle, not per polygon: a sculpted terrain is full of warped quads, and
        a warped quad's vertex average can sit below its own surface, so a ray from there hits the
        quad itself. A triangle's centroid always lies on the triangle.
        """
        mesh = obj.data
        matrix = obj.matrix_world
        verts = np.empty(len(mesh.vertices) * 3, dtype=np.float64)
        mesh.vertices.foreach_get("co", verts)
        verts = verts.reshape(-1, 3)
        verts = verts @ np.array(matrix.to_3x3()).T + np.array(matrix.translation)

        mesh.calc_loop_triangles()
        tris = np.empty(len(mesh.loop_triangles) * 3, dtype=np.int64)
        mesh.loop_triangles.foreach_get("vertices", tris)
        tris = tris.reshape(-1, 3)
        tri_polygons = np.empty(len(mesh.loop_triangles), dtype=np.int64)
        mesh.loop_triangles.foreach_get("polygon_index", tri_polygons)
        if not len(tris):
            return verts, tris

        corners = verts[tris]
        normals = np.cross(corners[:, 1] - corners[:, 0], corners[:, 2] - corners[:, 0])
        lengths = np.linalg.norm(normals, axis=1)
        is_flat_enough = np.abs(normals[:, 2]) > TOP_FACE_NORMAL_THRESHOLD * lengths
        centroids = corners.mean(axis=1)

        bvh = BVHTree.FromPolygons(verts.tolist(), tris.tolist())
        is_top = np.zeros(len(tris), dtype=bool)
        for i in np.flatnonzero(is_flat_enough):
            is_top[i] = cls.is_visible_from_above(bvh, Vector(centroids[i]), tri_polygons, tri_polygons[i])
        return verts, tris[is_top]

    @classmethod
    def is_visible_from_above(
        cls, bvh: BVHTree, location: Vector, tri_polygons: np.ndarray, polygon_index: int
    ) -> bool:
        """Whether nothing lies directly above ``location``, ignoring the triangle's own polygon."""
        up = Vector((0.0, 0.0, 1.0))
        # A warped polygon can fold over its own triangles; step past those hits.
        for _ in range(8):
            hit, _, index, _ = bvh.ray_cast(location + up * 1e-4, up)
            if hit is None:
                return True
            if tri_polygons[index] != polygon_index:
                return False
            location = hit
        return False

    @classmethod
    def slice_triangles(cls, verts: np.ndarray, tris: np.ndarray, z: float) -> list[Polyline]:
        """Intersect a triangle mesh with the horizontal plane at ``z`` and chain the result.

        A vertex exactly at ``z`` counts as above the plane, so no triangle is ever cut through
        a vertex and every crossing point lies strictly inside an edge. Crossing points are keyed
        by their edge, which is how segments from neighbouring triangles join up.
        """
        tri_z = verts[tris, 2]
        crossing = (tri_z.min(axis=1) < z) & (tri_z.max(axis=1) >= z)
        if not crossing.any():
            return []

        points: dict[tuple[int, int], np.ndarray] = {}
        segments: list[tuple[tuple[int, int], tuple[int, int]]] = []
        for tri in tris[crossing]:
            keys = []
            for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
                if (verts[a, 2] >= z) == (verts[b, 2] >= z):
                    continue
                key = (int(a), int(b)) if a < b else (int(b), int(a))
                if key not in points:
                    pa, pb = verts[key[0]], verts[key[1]]
                    t = (z - pa[2]) / (pb[2] - pa[2])
                    point = pa + (pb - pa) * t
                    point[2] = z
                    points[key] = point
                keys.append(key)
            if len(keys) == 2:
                segments.append((keys[0], keys[1]))

        polylines = []
        for chain, closed in cls.chain_segments(segments):
            # A level that passes exactly through a vertex gives the same point on
            # every edge leaving that vertex, so drop the zero-length steps.
            coords = np.array([points[k] for k in chain])
            keep = np.ones(len(coords), dtype=bool)
            keep[1:] = np.any(np.abs(np.diff(coords, axis=0)) > 1e-9, axis=1)
            coords = coords[keep]
            if closed and len(coords) > 1 and np.allclose(coords[0], coords[-1], atol=1e-9):
                coords = coords[:-1]
            if len(coords) >= 2:
                polylines.append((coords, closed and len(coords) >= 3))
        return polylines

    @classmethod
    def chain_segments(cls, segments: list[tuple]) -> list[tuple[list, bool]]:
        """Join segments that share endpoints into ordered chains of keys.

        :return: (keys in order, is closed) per chain. Open chains are walked from a free end
            first, so a contour that runs off the edge of the terrain is one polyline, not two.
        """
        adjacency: dict = {}
        for i, (a, b) in enumerate(segments):
            adjacency.setdefault(a, []).append(i)
            adjacency.setdefault(b, []).append(i)

        used = [False] * len(segments)

        def walk(start) -> list:
            chain = [start]
            current = start
            while True:
                next_segment = next((i for i in adjacency[current] if not used[i]), None)
                if next_segment is None:
                    return chain
                used[next_segment] = True
                a, b = segments[next_segment]
                current = b if a == current else a
                chain.append(current)

        chains = []
        free_ends = [key for key, segment_ids in adjacency.items() if len(segment_ids) == 1]
        for key in free_ends:
            if any(not used[i] for i in adjacency[key]):
                chains.append((walk(key), False))
        for i, (a, _) in enumerate(segments):
            if not used[i]:
                chain = walk(a)
                is_closed = len(chain) > 2 and chain[0] == chain[-1]
                chains.append((chain[:-1] if is_closed else chain, is_closed))
        return chains

    @classmethod
    def get_contour_context(cls) -> ifcopenshell.entity_instance:
        ifc_file = tool.Ifc.get()
        context = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Annotation", "MODEL_VIEW")
        if context:
            return context
        parent = ifcopenshell.util.representation.get_context(ifc_file, "Model")
        return ifcopenshell.api.context.add_context(
            ifc_file, context_type="Model", context_identifier="Annotation", target_view="MODEL_VIEW", parent=parent
        )

    @classmethod
    def create_contour(
        cls,
        terrain: ifcopenshell.entity_instance,
        elevation: float,
        z: float,
        polylines: list[Polyline],
        is_index: bool,
    ) -> ifcopenshell.entity_instance:
        """Create one IfcAnnotation CONTOURLINE holding every polyline at one elevation.

        :param elevation: Project elevation in SI metres, stored as the ContourValue.
        :param z: Blender world Z of the contour, used as the annotation's placement.
        """
        ifc_file = tool.Ifc.get()
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        elevation_label = f"{round(elevation / unit_scale, 6):g}"

        terrain_obj = tool.Ifc.get_object(terrain)
        origin = Vector((terrain_obj.matrix_world.translation.x, terrain_obj.matrix_world.translation.y, z))
        obj = bpy.data.objects.new(f"Contour {elevation_label}", bpy.data.meshes.new("Mesh"))
        obj.matrix_world = Matrix.Translation(origin)

        contour = bonsai.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class="IfcAnnotation",
            predefined_type="CONTOURLINE",
            should_add_representation=False,
        )
        tool.Geometry.run_edit_object_placement(obj)

        builder = ShapeBuilder(ifc_file)
        origin_np = np.array(origin)
        items = [builder.polyline((points - origin_np) / unit_scale, closed=closed) for points, closed in polylines]
        representation = builder.get_representation(cls.get_contour_context(), items)
        ifcopenshell.api.geometry.assign_representation(ifc_file, contour, representation)
        bonsai.core.geometry.switch_representation(tool.Ifc, tool.Geometry, obj=obj, representation=representation)

        pset = ifcopenshell.api.pset.add_pset(ifc_file, product=contour, name="Pset_AnnotationContourLine")
        ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties={"ContourValue": elevation / unit_scale})
        if is_index:
            pset = ifcopenshell.api.pset.add_pset(ifc_file, product=contour, name="EPset_Annotation")
            ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties={"Classes": "IndexContour"})

        ifcopenshell.api.drawing.assign_product(ifc_file, relating_product=terrain, related_object=contour)
        cls.place_contour_with_terrain(terrain, contour, obj)
        return contour

    @classmethod
    def place_contour_with_terrain(
        cls, terrain: ifcopenshell.entity_instance, contour: ifcopenshell.entity_instance, obj: bpy.types.Object
    ) -> None:
        # assign_class skips spatial containment for annotations while a drawing is
        # active, so contain the contour explicitly alongside its terrain.
        container = ifcopenshell.util.element.get_container(terrain)
        if not container and terrain.is_a("IfcSpatialElement"):
            container = terrain
        if container:
            ifcopenshell.api.spatial.assign_container(tool.Ifc.get(), products=[contour], relating_structure=container)
            tool.Collector.assign(obj)
