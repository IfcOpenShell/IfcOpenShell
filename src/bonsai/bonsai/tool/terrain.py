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
from dataclasses import dataclass
from typing import TYPE_CHECKING, Union

import bpy
import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.drawing
import ifcopenshell.api.geometry
import ifcopenshell.api.group
import ifcopenshell.api.pset
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.type
import ifcopenshell.util.element
import ifcopenshell.util.geolocation
import ifcopenshell.util.representation
import ifcopenshell.util.unit
import numpy as np
import shapely
import shapely.affinity
from ifcopenshell.util.shape_builder import ShapeBuilder
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

import bonsai.core.root
import bonsai.core.tool
import bonsai.tool as tool

if TYPE_CHECKING:
    from bonsai.bim.module.terrain.prop import BIMTerrainProperties


# A polyline as an (N, 3) array of points, and whether it closes on itself.
Polyline = tuple[np.ndarray, bool]

CONTOUR_PSET = "BBIM_Contours"
LABEL_PSET = "BBIM_ContourLabel"
MAX_CONTOUR_LEVELS = 2000
# Faces steeper than this (|normal.z| below it) are treated as walls, not terrain.
TOP_FACE_NORMAL_THRESHOLD = 0.1


@dataclass
class ElevationDatum:
    """Maps Blender world Z (SI) to the height contours are cut and labelled at (SI)."""

    source: Union[str, None]
    # Datum height of the project origin (project Z = 0).
    origin_height: float
    # Datum height change per unit of project Z (map conversion FactorZ, normally 1).
    slope: float
    # Project Z minus Blender Z.
    blender_offset: float

    def to_height(self, z):
        return self.origin_height + self.slope * (z + self.blender_offset)

    def to_z(self, height):
        return (height - self.origin_height) / self.slope - self.blender_offset


class Terrain(bonsai.core.tool.Terrain):
    @classmethod
    def get_terrain_props(cls) -> BIMTerrainProperties:
        return bpy.context.scene.BIMTerrainProperties

    @classmethod
    def is_terrain(cls, element: ifcopenshell.entity_instance) -> bool:
        if element.is_a("IfcSite"):
            return True
        return (
            element.is_a("IfcGeographicElement") and ifcopenshell.util.element.get_predefined_type(element) == "TERRAIN"
        )

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
        # A label without its contour would show an empty value.
        for label in cls.get_contour_labels(contour):
            cls.remove_contour_label(label)
        if obj := tool.Ifc.get_object(contour):
            tool.Geometry.delete_ifc_object(obj)
        else:
            ifcopenshell.api.root.remove_product(tool.Ifc.get(), product=contour)

    @classmethod
    def get_contour_elevation(cls, contour: ifcopenshell.entity_instance) -> Union[float, None]:
        """The contour's ContourValue in SI metres."""
        value = ifcopenshell.util.element.get_pset(contour, "Pset_AnnotationContourLine", "ContourValue")
        if value is None:
            return None
        return value * ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())

    @classmethod
    def get_blender_offset_z(cls) -> float:
        """SI offset to add to a Blender Z to get the project (IFC) Z."""
        if not tool.Georeference.has_blender_offset():
            return 0.0
        props = tool.Georeference.get_georeference_props()
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        return float(props.blender_offset_z) * unit_scale

    @classmethod
    def get_datum(cls, element: ifcopenshell.entity_instance) -> ElevationDatum:
        """How Blender Z maps to the height contours are cut and labelled at.

        Surveys give heights above a vertical datum (e.g. sea level), not above the project
        origin. That datum comes from the map conversion's OrthogonalHeight if the project is
        georeferenced, otherwise from the site's RefElevation, otherwise there is none.
        """
        ifc_file = tool.Ifc.get()
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        blender_offset = cls.get_blender_offset_z()
        if ifcopenshell.util.geolocation.get_helmert_transformation_parameters(ifc_file):
            # auto_z2e is linear in z, so two samples give its slope and origin height.
            origin = ifcopenshell.util.geolocation.auto_z2e(ifc_file, 0.0, should_return_in_map_units=False)
            slope = ifcopenshell.util.geolocation.auto_z2e(ifc_file, 1.0, should_return_in_map_units=False) - origin
            return ElevationDatum("Map Conversion", origin * unit_scale, slope, blender_offset)
        if (site := cls.get_site(element)) and site.RefElevation:
            return ElevationDatum("Site RefElevation", site.RefElevation * unit_scale, 1.0, blender_offset)
        return ElevationDatum(None, 0.0, 1.0, blender_offset)

    @classmethod
    def get_site(cls, element: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        current = element
        while current:
            if current.is_a("IfcSite"):
                return current
            current = ifcopenshell.util.element.get_container(current) or ifcopenshell.util.element.get_aggregate(
                current
            )
        sites = tool.Ifc.get().by_type("IfcSite")
        return sites[0] if len(sites) == 1 else None

    @classmethod
    def get_contour_levels(
        cls, element: ifcopenshell.entity_instance, interval: float
    ) -> list[tuple[int, float, list[Polyline]]]:
        """Slice the terrain's top surface every ``interval`` (SI) metres of datum height.

        :return: (level index, Blender world Z, polylines in Blender world coordinates) per
            elevation that has at least one contour. The datum height is ``index * interval``.
        """
        obj = tool.Ifc.get_object(element)
        if not isinstance(obj, bpy.types.Object) or not isinstance(obj.data, bpy.types.Mesh):
            return []
        verts, tris = cls.get_top_surface_triangles(obj)
        if not len(tris):
            return []

        datum = cls.get_datum(element)
        heights = datum.to_height(verts[np.unique(tris), 2])
        first = math.ceil(heights.min() / interval)
        last = math.floor(heights.max() / interval)
        if last - first + 1 > MAX_CONTOUR_LEVELS:
            raise ValueError(
                f"An interval of {interval}m would create {last - first + 1} contours. "
                f"Use a larger interval (at most {MAX_CONTOUR_LEVELS} contours)."
            )

        levels = []
        for i in range(first, last + 1):
            z = datum.to_z(i * interval)
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
    def place_labels(
        cls,
        polylines: list[np.ndarray],
        lengths: list[float],
        height: float,
        spacing: float,
        bounds: tuple[float, float, float, float],
        obstacles: list = (),
    ) -> list[tuple[int, float, float, float]]:
        """Choose where to put a label along each 2D polyline.

        Labels are spread evenly, about every ``spacing``. Near each target spot the label slides
        to where the line is straightest over its length, must sit fully inside ``bounds`` and must
        not overlap a label already placed or an obstacle. Angles are kept readable: never
        upside down.

        :param polylines: (N, 2) points per polyline, in the drawing plane.
        :param lengths: Label length per polyline (its text width), same units as the points.
        :param height: Label height.
        :param bounds: (min x, min y, max x, max y) of the drawing frame.
        :param obstacles: shapely geometries labels must not overlap.
        :return: (polyline index, x, y, angle in degrees) per label.
        """
        frame = shapely.box(*bounds)
        placed = list(obstacles)
        labels = []
        for index, (points, length) in enumerate(zip(polylines, lengths)):
            if len(points) < 2:
                continue
            distances = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(points, axis=0), axis=1))])
            total = distances[-1]
            if total < length * 1.5:
                continue

            def point_at(s):
                return np.array([np.interp(s, distances, points[:, 0]), np.interp(s, distances, points[:, 1])])

            count = max(1, int(total // spacing))
            window = min(spacing, total) / 4
            for target in (np.arange(count) + 0.5) * total / count:
                best = None
                for centre in np.linspace(target - window, target + window, 9):
                    start, end = centre - length / 2, centre + length / 2
                    if start < 0 or end > total:
                        continue
                    a, b = point_at(start), point_at(end)
                    chord = b - a
                    chord_length = np.linalg.norm(chord)
                    if chord_length < length * 0.8:
                        continue  # Too curvy for the text to sit on.
                    direction = chord / chord_length
                    inside = points[(distances > start) & (distances < end)]
                    offsets = inside - a
                    deviation = np.abs(offsets[:, 0] * direction[1] - offsets[:, 1] * direction[0]).max(initial=0.0)
                    x, y = point_at(centre)
                    angle = math.degrees(math.atan2(direction[1], direction[0]))
                    if angle > 90:
                        angle -= 180
                    elif angle <= -90:
                        angle += 180
                    box = shapely.affinity.translate(
                        shapely.affinity.rotate(shapely.box(-length / 2, -height / 2, length / 2, height / 2), angle),
                        x,
                        y,
                    )
                    if not frame.contains(box) or any(box.intersects(p) for p in placed):
                        continue
                    score = deviation + abs(centre - target) * 0.01
                    if best is None or score < best[0]:
                        best = (score, x, y, angle, box)
                if best:
                    placed.append(best[4])
                    labels.append((index, float(best[1]), float(best[2]), best[3]))
        return labels

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

        :param elevation: Datum height in SI metres, stored as the ContourValue.
        :param z: Blender world Z of the contour, used as the annotation's placement.
        """
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
        obj = bpy.data.objects.new(f"Contour {round(elevation / unit_scale, 6):g}", bpy.data.meshes.new("Mesh"))
        contour = bonsai.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class="IfcAnnotation",
            predefined_type="CONTOURLINE",
            should_add_representation=False,
        )
        ifcopenshell.api.drawing.assign_product(tool.Ifc.get(), relating_product=terrain, related_object=contour)
        cls.place_contour_with_terrain(terrain, contour, obj)
        cls.update_contour(contour, terrain, elevation, z, polylines, is_index)
        return contour

    @classmethod
    def update_contour(
        cls,
        contour: ifcopenshell.entity_instance,
        terrain: ifcopenshell.entity_instance,
        elevation: float,
        z: float,
        polylines: list[Polyline],
        is_index: bool,
    ) -> None:
        """Replace a contour's geometry and data in place, keeping the same annotation.

        Anything pointing at the contour, such as a label, stays linked across an Update.
        """
        ifc_file = tool.Ifc.get()
        unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
        obj = tool.Ifc.get_object(contour)
        terrain_obj = tool.Ifc.get_object(terrain)
        origin = Vector((terrain_obj.matrix_world.translation.x, terrain_obj.matrix_world.translation.y, z))
        obj.matrix_world = Matrix.Translation(origin)
        tool.Geometry.run_edit_object_placement(obj)

        builder = ShapeBuilder(ifc_file)
        origin_np = np.array(origin)
        items = [builder.polyline((points - origin_np) / unit_scale, closed=closed) for points, closed in polylines]
        context = cls.get_contour_context()
        tool.Model.replace_object_ifc_representation(context, obj, builder.get_representation(context, items))

        pset = tool.Pset.get_element_pset(contour, "Pset_AnnotationContourLine")
        if not pset:
            pset = ifcopenshell.api.pset.add_pset(ifc_file, product=contour, name="Pset_AnnotationContourLine")
        ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties={"ContourValue": elevation / unit_scale})

        # Only touch the IndexContour token, so classes a user added survive an Update.
        pset = tool.Pset.get_element_pset(contour, "EPset_Annotation")
        classes = (ifcopenshell.util.element.get_pset(contour, "EPset_Annotation", "Classes") or "").split()
        new_classes = [c for c in classes if c != "IndexContour"] + (["IndexContour"] if is_index else [])
        if new_classes == classes:
            return
        if not pset:
            pset = ifcopenshell.api.pset.add_pset(ifc_file, product=contour, name="EPset_Annotation")
        ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties={"Classes": " ".join(new_classes) or None})

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

    @classmethod
    def get_selected_terrain(cls, obj: Union[bpy.types.Object, None]) -> Union[ifcopenshell.entity_instance, None]:
        if obj and (element := tool.Ifc.get_entity(obj)) and cls.is_terrain(element):
            return element

    @classmethod
    def get_active_drawing(cls) -> Union[ifcopenshell.entity_instance, None]:
        camera = bpy.context.scene.camera
        if camera and (drawing := tool.Ifc.get_entity(camera)) and drawing.ObjectType == "DRAWING":
            return drawing

    @classmethod
    def get_contour_labels(
        cls, contour: ifcopenshell.entity_instance, drawing: Union[ifcopenshell.entity_instance, None] = None
    ) -> list[ifcopenshell.entity_instance]:
        """Generated labels of a contour, optionally only those in one drawing."""
        labels = []
        for rel in getattr(contour, "ReferencedBy", []) or []:
            if not rel.is_a("IfcRelAssignsToProduct"):
                continue
            for label in rel.RelatedObjects:
                if not ifcopenshell.util.element.get_pset(label, LABEL_PSET):
                    continue
                if drawing and tool.Drawing.get_annotation_drawing(label) != drawing:
                    continue
                labels.append(label)
        return labels

    @classmethod
    def remove_contour_label(cls, label: ifcopenshell.entity_instance) -> None:
        if obj := tool.Ifc.get_object(label):
            tool.Geometry.delete_ifc_object(obj)
        else:
            ifcopenshell.api.root.remove_product(tool.Ifc.get(), product=label)

    @classmethod
    def get_label_signature(cls, matrix: Matrix) -> str:
        angle = math.degrees(math.atan2(matrix[1][0], matrix[0][0]))
        return f"{matrix.translation.x:.4f},{matrix.translation.y:.4f},{angle:.2f}"

    @classmethod
    def is_label_moved(cls, label: ifcopenshell.entity_instance) -> bool:
        """Whether a label is no longer where it was generated, i.e. the user placed it."""
        obj = tool.Ifc.get_object(label)
        placed = ifcopenshell.util.element.get_pset(label, LABEL_PSET, "Placement")
        return bool(obj and placed and placed != cls.get_label_signature(obj.matrix_world))

    @classmethod
    def get_label_font_size(cls, relating_type: Union[ifcopenshell.entity_instance, None]) -> float:
        """Paper font height in mm, from the type's font size class (Bonsai's default is regular)."""
        from bonsai.bim.module.drawing.data import FONT_SIZES

        classes = ""
        if relating_type:
            classes = ifcopenshell.util.element.get_pset(relating_type, "EPset_Annotation", "Classes") or ""
        for name in classes.split():
            if name in FONT_SIZES:
                return FONT_SIZES[name]
        return FONT_SIZES["regular"]

    @classmethod
    def get_label_template(cls, element: ifcopenshell.entity_instance) -> str:
        """Label text that reads the contour's own ContourValue, rounded to the interval's precision."""
        nearest = "1"
        if settings := cls.get_contour_settings(element):
            interval = settings[0] / ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
            for places in range(1, 4):
                if abs(interval - round(interval)) < 1e-6:
                    break
                interval *= 10
                nearest = f"{10**-places:.{places}f}"
        return "``round({{Pset_AnnotationContourLine.ContourValue}}, " + nearest + ")``"

    @classmethod
    def get_label_placements(
        cls,
        element: ifcopenshell.entity_instance,
        drawing: ifcopenshell.entity_instance,
        relating_type: Union[ifcopenshell.entity_instance, None],
        spacing: float,
        kept_labels: list[ifcopenshell.entity_instance],
    ) -> list[tuple[ifcopenshell.entity_instance, Matrix]]:
        """Where to put labels on the terrain's contours in a plan drawing.

        :param spacing: Distance between labels along a contour, in SI metres.
        :param kept_labels: Labels the user moved; new labels keep clear of them.
        :return: (contour, label world matrix) per label.
        """
        camera = tool.Ifc.get_object(drawing)
        camera_matrix = tool.Drawing.get_camera_matrix(camera)
        to_camera = camera_matrix.inverted()
        scale = ifcopenshell.util.element.get_pset(drawing, "EPset_Drawing", "Scale") or "1/100"
        paper_to_model = 1 / 1000 / tool.Drawing.get_scale_ratio(scale)
        font_size = cls.get_label_font_size(relating_type)
        height = (font_size + 1.0) * paper_to_model

        def label_length(contour: ifcopenshell.entity_instance) -> float:
            value = ifcopenshell.util.element.get_pset(contour, "Pset_AnnotationContourLine", "ContourValue") or 0
            return (len(f"{value:g}") * 0.6 * font_size + 2.0) * paper_to_model

        corners = [to_camera @ Vector(v) for v in tool.Drawing.get_camera_block(camera)["verts"]]
        bounds = (
            min(v.x for v in corners),
            min(v.y for v in corners),
            max(v.x for v in corners),
            max(v.y for v in corners),
        )

        contours, polylines, lengths = [], [], []
        for contour in cls.get_contours(element):
            obj = tool.Ifc.get_object(contour)
            if not obj or not isinstance(obj.data, bpy.types.Mesh):
                continue
            coords = [(to_camera @ (obj.matrix_world @ v.co)).xy for v in obj.data.vertices]
            for keys, closed in cls.chain_segments([tuple(e.vertices) for e in obj.data.edges]):
                points = np.array([coords[k] for k in keys])
                if closed:
                    points = np.vstack([points, points[:1]])
                contours.append(contour)
                polylines.append(points)
                lengths.append(label_length(contour))

        obstacles = []
        for label in kept_labels:
            label_obj = tool.Ifc.get_object(label)
            contour = tool.Drawing.get_assigned_product(label)
            if not label_obj or not contour:
                continue
            local = to_camera @ label_obj.matrix_world
            angle = math.degrees(math.atan2(local[1][0], local[0][0]))
            length = label_length(contour)
            box = shapely.affinity.rotate(shapely.box(-length / 2, -height / 2, length / 2, height / 2), angle)
            obstacles.append(shapely.affinity.translate(box, local.translation.x, local.translation.y))

        # Annotations sit just in front of the camera's clipping plane, as Bonsai places them.
        z = -(camera.data.clip_start + 0.05)
        placements = []
        for index, x, y, angle in cls.place_labels(polylines, lengths, height, spacing, bounds, obstacles):
            matrix = camera_matrix @ Matrix.Translation((x, y, z)) @ Matrix.Rotation(math.radians(angle), 4, "Z")
            placements.append((contours[index], matrix))
        return placements

    @classmethod
    def create_contour_label(
        cls,
        drawing: ifcopenshell.entity_instance,
        contour: ifcopenshell.entity_instance,
        matrix: Matrix,
        relating_type: Union[ifcopenshell.entity_instance, None],
        template: str,
    ) -> ifcopenshell.entity_instance:
        """Create a TEXT annotation in the drawing that shows the contour's elevation.

        With a text type that has its own text, that text is the template (mapped from the type);
        otherwise the label gets ``template``. Without a type, the label is styled ``fill-bg
        ContourLabel`` itself; with one, styling comes from the type.
        """
        ifc_file = tool.Ifc.get()
        obj = bpy.data.objects.new("Contour Label", None)
        obj.matrix_world = matrix
        label = bonsai.core.root.assign_class(
            tool.Ifc,
            tool.Collector,
            tool.Root,
            obj=obj,
            ifc_class="IfcAnnotation",
            predefined_type="TEXT",
            should_add_representation=False,
        )
        target_view = tool.Drawing.get_drawing_target_view(drawing)
        context = tool.Drawing.get_annotation_context(target_view, "TEXT") or tool.Drawing.create_annotation_context(
            target_view, "TEXT"
        )
        if relating_type:
            ifcopenshell.api.type.assign_type(ifc_file, related_objects=[label], relating_type=relating_type)
        if not (representation := tool.Drawing.get_representation(label, context)):
            literal = tool.Drawing.add_literal(Literal=template, BoxAlignment="center")
            representation = ifc_file.createIfcShapeRepresentation(context, "Annotation", "Annotation2D", [literal])
            ifcopenshell.api.geometry.assign_representation(ifc_file, product=label, representation=representation)
        if not relating_type:
            pset = ifcopenshell.api.pset.add_pset(ifc_file, product=label, name="EPset_Annotation")
            ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties={"Classes": "fill-bg ContourLabel"})

        ifcopenshell.api.group.assign_group(ifc_file, group=tool.Drawing.get_drawing_group(drawing), products=[label])
        ifcopenshell.api.drawing.assign_product(ifc_file, relating_product=contour, related_object=label)
        tool.Geometry.run_edit_object_placement(obj)
        pset = ifcopenshell.api.pset.add_pset(ifc_file, product=label, name=LABEL_PSET)
        signature = cls.get_label_signature(obj.matrix_world)
        ifcopenshell.api.pset.edit_pset(ifc_file, pset=pset, properties={"Placement": signature})
        tool.Collector.assign(obj)
        tool.Drawing.reload_representation(obj, representation)
        return label
