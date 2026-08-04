# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2026 Dion Moult <dion@thinkmoult.com>
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

"""Blender-independent utilities for space geometry generation.

These functions operate on IFC geometry data (vertices, faces, element
relationships) without requiring any Blender objects to be loaded. They are
used by Bonsai's space generation pipeline but can also be used standalone
for IFC analysis.
"""

from __future__ import annotations

from typing import Literal, Optional, Union

import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.boundary
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
import ifcopenshell.util.shape
import ifcopenshell.util.shape_builder
import ifcopenshell.util.unit
import numpy as np
import shapely

BOUNDING_CLASSES = ("IfcWall", "IfcColumn", "IfcMember", "IfcVirtualElement", "IfcPlate")
HEIGHT_DETECTION_CLASSES = ("IfcSlab", "IfcRoof")


def get_boundary_lines(
    ifc_file: ifcopenshell.file,
    shapes: dict,
    cut_z: float,
    bounding_classes: tuple = BOUNDING_CLASSES,
) -> tuple[list[shapely.LineString], list[ifcopenshell.entity_instance]]:
    """Generate boundary lines by bisecting IFC element geometry with a horizontal plane.

    :param ifc_file: The IFC file.
    :param shapes: Dict of element shapes keyed by element id, as produced by
        a geometry cache. Each entry must have ``verts`` (n,3 ndarray),
        ``faces`` (m,3 ndarray), ``bottom_z`` (float), ``top_z`` (float).
    :param cut_z: Z elevation of the cutting plane in world coordinates.
    :param bounding_classes: IFC classes to treat as space-bounding elements.
    :return: ``(boundary_lines, bounding_elements)`` where boundary_lines is a
        list of shapely LineString segments and bounding_elements is a list of
        IFC entity instances that intersect the cutting plane.
    """
    boundary_lines: list[shapely.LineString] = []
    bounding_elements: list[ifcopenshell.entity_instance] = []

    for element_id, shape_data in shapes.items():
        element = ifc_file.by_id(element_id)
        if not any(element.is_a(cls) for cls in bounding_classes):
            continue
        if cut_z <= shape_data["bottom_z"] or cut_z >= shape_data["top_z"]:
            continue
        bounding_elements.append(element)
        segments = ifcopenshell.util.shape.bisect_mesh_plane_vf(
            shape_data["verts"], shape_data["faces"], cut_z, precision=3, extend=0.05
        )
        for start, end in segments:
            boundary_lines.append(shapely.LineString([start, end]))

    return boundary_lines, bounding_elements


def get_space_polygon(
    boundary_lines: list[shapely.LineString],
    x: float,
    y: float,
) -> tuple[Union[shapely.Polygon, str], list]:
    """Assemble boundary lines into closed polygons and find the one containing (x, y).

    :param boundary_lines: List of shapely LineString segments forming a planar graph.
    :param x: X coordinate of the point to test.
    :param y: Y coordinate of the point to test.
    :return: ``(polygon, [])`` on success, or ``("NO POLYGONS FOUND", [])`` /
        ``("NO POLYGON FOR POINT", [])`` on failure. The second element is
        reserved for bounding elements (returned by the caller from
        :func:`get_boundary_lines`).
    """
    unioned = shapely.union_all(shapely.GeometryCollection(boundary_lines))
    closed_polygons = shapely.polygonize(unioned.geoms)
    if not closed_polygons:
        return "NO POLYGONS FOUND", []
    for polygon in closed_polygons.geoms:
        if shapely.contains_xy(polygon, x, y):
            return shapely.force_3d(polygon), []
    return "NO POLYGON FOR POINT", []


def get_auto_space_height(
    ifc_file: ifcopenshell.file,
    shapes: dict,
    space_polygon: shapely.Polygon,
    base_z: float,
    bounding_walls: list[ifcopenshell.entity_instance],
) -> Optional[float]:
    """Auto-detect space height from elements above using IFC geometry.

    Detection priority:
    1. ``IfcRelConnectsElements`` (TOP) connections on bounding walls
    2. ``IfcSlab`` / ``IfcRoof`` elements above with XY overlap to the space polygon
    3. Minimum wall top Z of bounding walls

    :param ifc_file: The IFC file.
    :param shapes: Dict of element shapes keyed by element id (see :func:`get_boundary_lines`).
    :param space_polygon: The space footprint polygon in world XY.
    :param base_z: The space's base Z in world coordinates.
    :param bounding_walls: List of IFC wall elements bounding the space.
    :return: Detected height in meters, or ``None`` if nothing found.
    """
    height = get_height_from_top_connections(ifc_file, shapes, bounding_walls, base_z, space_polygon)
    if height is not None and height > 0:
        return height

    height = get_height_from_elements_above(ifc_file, shapes, space_polygon, base_z)
    if height is not None and height > 0:
        return height

    height = get_height_from_wall_tops(shapes, bounding_walls, base_z)
    if height is not None and height > 0:
        return height

    return None


def get_height_from_top_connections(
    ifc_file: ifcopenshell.file,
    shapes: dict,
    bounding_walls: list[ifcopenshell.entity_instance],
    base_z: float,
    space_polygon: shapely.Polygon,
) -> Optional[float]:
    """Find the lowest bottom face of elements connected to bounding walls via IfcRelConnectsElements(TOP).

    :param ifc_file: The IFC file.
    :param shapes: Dict of element shapes keyed by element id.
    :param bounding_walls: List of IFC wall elements.
    :param base_z: The space's base Z in world coordinates.
    :param space_polygon: The space footprint polygon in world XY.
    :return: Height in meters, or ``None``.
    """
    lowest_min_z: Optional[float] = None
    for wall_element in bounding_walls:
        for connected_element, _rel in ifcopenshell.util.element.iter_top_connections(wall_element):
            if not (connected_element.is_a("IfcSlab") or connected_element.is_a("IfcRoof")):
                continue
            shape_data = shapes.get(connected_element.id())
            if not shape_data:
                continue
            min_z = shape_data["bottom_z"]
            if min_z <= base_z:
                continue
            verts = shape_data["verts"]
            element_box = shapely.box(
                float(verts[:, 0].min()),
                float(verts[:, 1].min()),
                float(verts[:, 0].max()),
                float(verts[:, 1].max()),
            )
            if not element_box.intersects(space_polygon):
                continue
            if lowest_min_z is None or min_z < lowest_min_z:
                lowest_min_z = min_z
    if lowest_min_z is not None:
        return lowest_min_z - base_z
    return None


def get_height_from_elements_above(
    ifc_file: ifcopenshell.file,
    shapes: dict,
    space_polygon: shapely.Polygon,
    base_z: float,
    height_classes: tuple = HEIGHT_DETECTION_CLASSES,
) -> Optional[float]:
    """Find the lowest IfcSlab / IfcRoof above whose XY bbox overlaps the space polygon.

    :param ifc_file: The IFC file.
    :param shapes: Dict of element shapes keyed by element id.
    :param space_polygon: The space footprint polygon in world XY.
    :param base_z: The space's base Z in world coordinates.
    :param height_classes: IFC classes to consider as ceiling elements.
    :return: Height in meters, or ``None``.
    """
    lowest_min_z: Optional[float] = None
    for ifc_class in height_classes:
        for element in ifc_file.by_type(ifc_class):
            shape_data = shapes.get(element.id())
            if not shape_data:
                continue
            min_z = shape_data["bottom_z"]
            if min_z <= base_z:
                continue
            verts = shape_data["verts"]
            element_box = shapely.box(
                float(verts[:, 0].min()),
                float(verts[:, 1].min()),
                float(verts[:, 0].max()),
                float(verts[:, 1].max()),
            )
            if not element_box.intersects(space_polygon):
                continue
            if lowest_min_z is None or min_z < lowest_min_z:
                lowest_min_z = min_z
    if lowest_min_z is not None:
        return lowest_min_z - base_z
    return None


def get_height_from_wall_tops(
    shapes: dict,
    bounding_walls: list[ifcopenshell.entity_instance],
    base_z: float,
) -> Optional[float]:
    """Find the minimum wall top Z among bounding walls.

    :param shapes: Dict of element shapes keyed by element id.
    :param bounding_walls: List of IFC wall elements.
    :param base_z: The space's base Z in world coordinates.
    :return: Height in meters, or ``None``.
    """
    lowest_top_z: Optional[float] = None
    for wall_element in bounding_walls:
        shape_data = shapes.get(wall_element.id())
        if not shape_data:
            continue
        max_z = shape_data["top_z"]
        if max_z <= base_z:
            continue
        if lowest_top_z is None or max_z < lowest_top_z:
            lowest_top_z = max_z
    if lowest_top_z is not None:
        return lowest_top_z - base_z
    return None


def _nearest_ray_hits(
    tree: ifcopenshell.geom.tree,
    origins: list[tuple[float, float, float]],
    ray_dir: np.ndarray,
) -> list[ifcopenshell.geom.hit]:
    """Nearest hit per origin; select_ray returns all hits including duplicates."""
    hits = []
    for origin in origins:
        results = sorted(tree.select_ray(origin, ray_dir, length=1e4), key=lambda h: h.distance)
        if results:
            hits.append(results[0])
    return hits


def get_vertical_bounding_planes(
    ifc_file: ifcopenshell.file,
    shapes: dict,
    tree: ifcopenshell.geom.tree,
    space_polygon: shapely.Polygon,
    base_z: float,
    direction: Literal["UP", "DOWN"],
    start_z: Optional[float] = None,
) -> tuple[str, list[tuple[np.ndarray, np.ndarray]]]:
    """Detect the top or bottom bounding planes for a space footprint.

    Rays are cast from ``start_z`` (the RL cut elevation passed by the Bonsai
    tool layer) so they start in the same horizontal slice of the room where
    the footprint polygon was found. When ``start_z`` is None, rays start at
    ``base_z + 0.001``.

    :param ifc_file: The IFC file.
    :param shapes: Cached element shapes keyed by element id.
    :param tree: Geometry tree with all bounding elements added.
    :param space_polygon: Space footprint in world XY.
    :param base_z: Base elevation of the space in SI.
    :param direction: "UP" for top (ceiling/roof) or "DOWN" for bottom (floor/slab).
    :param start_z: Elevation to cast rays from in SI (the RL cut level).
    :return: (strategy, planes). Strategy is always "EXTRUDE_CLIP"; an empty
        planes list means open top (direction="UP") or void below
        (direction="DOWN"). The strategy decision between extrusion and B-rep
        happens in the calling layer. Planes are (point, normal) tuples in SI;
        the normal points toward the removed side (half-space convention).
    """
    ray_dir = np.array([0.0, 0.0, 1.0]) if direction == "UP" else np.array([0.0, 0.0, -1.0])
    origin_z = start_z if start_z is not None else base_z + 0.001

    bounds = space_polygon.bounds
    cx = (bounds[0] + bounds[2]) / 2.0
    cy = (bounds[1] + bounds[3]) / 2.0
    sample_points = [(cx, cy)]
    if bounds[2] - bounds[0] > 0.1:
        sample_points.append((cx + 0.25 * (bounds[2] - bounds[0]), cy))
        sample_points.append((cx - 0.25 * (bounds[2] - bounds[0]), cy))
    if bounds[3] - bounds[1] > 0.1:
        sample_points.append((cx, cy + 0.25 * (bounds[3] - bounds[1])))
        sample_points.append((cx, cy - 0.25 * (bounds[3] - bounds[1])))

    # Sample from footprint corners, offset toward centroid so the ray origin
    # sits inside the space (not on a bounding wall).  This catches elements
    # (e.g. sloped roofs) that only cover a corner of the space.
    for coords in space_polygon.exterior.coords[:-1]:
        vx, vy = coords[0], coords[1]
        sample_points.append((vx + 0.05 * (cx - vx), vy + 0.05 * (cy - vy)))

    hits = _nearest_ray_hits(tree, [(x, y, origin_z) for x, y in sample_points], ray_dir)
    if not hits:
        return "EXTRUDE_CLIP", []  # open top / void below: no bounding planes

    tol_floor = 0.05
    plane_hits = []
    for result in hits:
        point = np.array(result.position, dtype=float)
        normal = np.array(result.normal, dtype=float)
        if abs(normal[2]) < 0.5:
            continue  # vertical face; not a top/bottom bounding plane
        if direction == "UP" and point[2] < base_z - tol_floor:
            continue  # RL below the space base: ignore hits under it
        if direction == "DOWN" and abs(point[2] - base_z) < tol_floor:
            continue  # flat floor at the space base: no bottom clip needed
        plane_hits.append((point, normal))

    tol_normal = 0.02
    tol_distance = 0.05
    plane_groups: list[tuple[np.ndarray, list[np.ndarray]]] = []
    for point, normal in plane_hits:
        added = False
        for anchor, members in plane_groups:
            plane_normal = np.array(members[0])
            if np.linalg.norm(normal - plane_normal) < tol_normal:
                if abs(np.dot(point - anchor, plane_normal)) < tol_distance:
                    members.append(normal)
                    added = True
                    break
        if not added:
            plane_groups.append((point, [normal]))

    planes = []
    for anchor, normals in plane_groups:
        mean_normal = np.mean(normals, axis=0)
        mean_normal /= np.linalg.norm(mean_normal)
        if np.dot(mean_normal, ray_dir) < 0:
            mean_normal = -mean_normal
        planes.append((anchor, mean_normal))

    return "EXTRUDE_CLIP", planes


def detect_space_volume_strategy(
    ifc_file: ifcopenshell.file,
    shapes: dict,
    tree: ifcopenshell.geom.tree,
    space_polygon: shapely.Polygon,
    base_z: float,
    bounding_walls: list[ifcopenshell.entity_instance],
    start_z: Optional[float] = None,
) -> tuple[str, Optional[list], Optional[list]]:
    """Decide whether a space can be represented as a clipped extrusion.

    A space is "EXTRUDE_CLIP" when all bounding walls have vertical side faces
    and the detected top/bottom bounding planes are few and piecewise-planar
    (0-2 top planes, 0-1 bottom plane). Otherwise it is "BREP".

    :param ifc_file: The IFC file.
    :param shapes: Cached element shapes.
    :param tree: Geometry tree with bounding elements.
    :param space_polygon: Space footprint in world XY.
    :param base_z: Base elevation in SI.
    :param bounding_walls: List of wall elements bounding the space.
    :param start_z: Ray-cast origin elevation (RL cut level) in SI.
    :return: ("EXTRUDE_CLIP", top_planes, bottom_planes) or ("BREP", None, None).
    """
    tol = 0.02
    for wall in bounding_walls:
        shape_data = shapes.get(wall.id())
        if not shape_data:
            continue
        verts = shape_data["verts"]
        faces = shape_data["faces"]
        if len(verts) == 0 or len(faces) == 0:
            continue
        v1 = verts[faces[:, 1]] - verts[faces[:, 0]]
        v2 = verts[faces[:, 2]] - verts[faces[:, 0]]
        normals = np.cross(v1, v2)
        norms = np.linalg.norm(normals, axis=1)
        normals = normals[norms > 1e-8]
        if len(normals) == 0:
            continue
        normals = normals / np.linalg.norm(normals, axis=1)[:, np.newaxis]
        side_mask = np.abs(normals[:, 2]) < 0.5
        if np.any(side_mask) and np.mean(np.abs(normals[side_mask, 2])) > tol:
            return "BREP", None, None

    _, top_planes = get_vertical_bounding_planes(ifc_file, shapes, tree, space_polygon, base_z, "UP", start_z=start_z)

    _, bottom_planes = get_vertical_bounding_planes(
        ifc_file, shapes, tree, space_polygon, base_z, "DOWN", start_z=start_z
    )

    if len(top_planes) > 2 or len(bottom_planes) > 1:
        return "BREP", None, None

    return "EXTRUDE_CLIP", top_planes, bottom_planes


def _footprint_coords(space_polygon: shapely.Polygon):
    """Yield (x, y) boundary coordinates of a footprint polygon (exterior then holes)."""
    for coords in [space_polygon.exterior.coords, *[ring.coords for ring in space_polygon.interiors]]:
        for point in coords:
            yield point[0], point[1]


def build_extruded_clipped_space(
    ifc_file: ifcopenshell.file,
    space_polygon: shapely.Polygon,
    base_z: float,
    top_planes: list[tuple[np.ndarray, np.ndarray]],
    bottom_planes: list[tuple[np.ndarray, np.ndarray]],
) -> ifcopenshell.entity_instance:
    """Build an IfcExtrudedAreaSolid clipped to top/bottom planes.

    :param ifc_file: The IFC file.
    :param space_polygon: Footprint polygon in world XY.
    :param base_z: Base elevation in SI.
    :param top_planes: List of (point, normal) tuples for top clipping planes.
    :param bottom_planes: List of (point, normal) tuples for bottom clipping planes.
    :return: IfcBooleanClippingResult chain.
    """
    builder = ifcopenshell.util.shape_builder.ShapeBuilder(ifc_file)
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)

    centroid = np.array([space_polygon.centroid.x, space_polygon.centroid.y])
    exterior = [
        (float(p[0] - centroid[0]) / unit_scale, float(p[1] - centroid[1]) / unit_scale)
        for p in space_polygon.exterior.coords[:-1]
    ]
    inner_curves = []
    for interior in space_polygon.interiors:
        inner = [
            (float(p[0] - centroid[0]) / unit_scale, float(p[1] - centroid[1]) / unit_scale)
            for p in interior.coords[:-1]
        ]
        inner_curve = builder.polyline(inner, closed=True)
        inner_curves.append(inner_curve)

    outer_curve = builder.polyline(exterior, closed=True)
    profile = builder.profile(outer_curve, inner_curves=inner_curves)

    all_z = [base_z]
    for point, normal in top_planes + bottom_planes:
        all_z.append(float(point[2]))
        for x, y in _footprint_coords(space_polygon):
            # A sloped plane's height varies across the footprint. The anchor
            # point is near the centre, so also cover the plane at the polygon
            # vertices, otherwise the high side of a sloped ceiling is capped
            # below the plane it should reach.
            if abs(normal[2]) < 1e-6:
                continue
            plane_z = (float(np.dot(normal, point)) - float(normal[0]) * x - float(normal[1]) * y) / float(normal[2])
            all_z.append(plane_z)
    min_z = min(all_z)
    max_z = max(all_z)
    height = max_z - min_z

    extrusion = builder.extrude(
        profile,
        magnitude=height / unit_scale,
        position=[(centroid[0] / unit_scale), (centroid[1] / unit_scale), min_z / unit_scale],
    )

    result = extrusion
    for point, normal in top_planes + bottom_planes:
        # clip_solid takes location in SI; it converts to project units internally.
        result = ifcopenshell.api.geometry.clip_solid(
            ifc_file,
            item=result,
            location=[float(point[i]) for i in range(3)],
            normal=[float(normal[i]) for i in range(3)],
        )

    return result


def _build_local_shapes(ifc_file: ifcopenshell.file) -> dict:
    """Build the local-coordinates shapes dict required by auto_generate_boundaries.

    Keys are element ids; values have ``verts`` (local), ``faces``, ``edges``
    and ``matrix`` as produced by ``ifcopenshell.geom.iterator``.
    """
    settings = ifcopenshell.geom.settings()
    settings.set("disable-opening-subtractions", True)
    shapes = {}
    iterator = ifcopenshell.geom.iterator(settings, ifc_file)
    if iterator.initialize():
        while True:
            shape = iterator.get()
            shapes[shape.id] = {
                "verts": ifcopenshell.util.shape.get_vertices(shape.geometry),
                "faces": ifcopenshell.util.shape.get_faces(shape.geometry),
                "edges": ifcopenshell.util.shape.get_edges(shape.geometry),
                "matrix": ifcopenshell.util.shape.get_shape_matrix(shape),
            }
            if not iterator.next():
                break
    return shapes


def build_brep_space(
    ifc_file: ifcopenshell.file,
    space: ifcopenshell.entity_instance,
    shapes: dict,
    space_polygon: shapely.Polygon,
    base_z: float,
) -> Union[ifcopenshell.entity_instance, None]:
    """Build a closed-shell B-rep space from auto-generated boundary faces.

    Seeds the space with a temporary extrusion spanning the bounding elements'
    vertical extent, generates 1st-level boundaries with
    ``auto_generate_boundaries``, then merges the boundary polygons into a
    closed mesh (``IfcFacetedBrep``/``IfcPolygonalFaceSet``).

    :param ifc_file: The IFC file.
    :param space: The IfcSpace entity.
    :param shapes: Cached element shapes (world coords) for the z-extent.
    :param space_polygon: Footprint polygon in world XY.
    :param base_z: Base elevation in SI.
    :return: IfcFacetedBrep or IfcPolygonalFaceSet, or None if boundaries
        cannot be resolved.
    """
    all_z = [base_z]
    for shape_data in shapes.values():
        all_z.append(shape_data["top_z"])
        all_z.append(shape_data["bottom_z"])
    min_z = min(all_z)
    max_z = max(all_z)
    height = max_z - min_z

    builder = ifcopenshell.util.shape_builder.ShapeBuilder(ifc_file)
    centroid = np.array([space_polygon.centroid.x, space_polygon.centroid.y])
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)
    exterior = [
        (float(p[0] - centroid[0]) / unit_scale, float(p[1] - centroid[1]) / unit_scale)
        for p in space_polygon.exterior.coords[:-1]
    ]
    outer_curve = builder.polyline(exterior, closed=True)
    profile = builder.profile(outer_curve)

    ctx = ifcopenshell.util.representation.get_context(ifc_file, "Model", "Body", "MODEL_VIEW")
    if ctx is None:
        return None

    seed = builder.extrude(
        profile,
        magnitude=height / unit_scale,
        position=[centroid[0] / unit_scale, centroid[1] / unit_scale, min_z / unit_scale],
    )
    seed_rep = builder.get_representation(ctx, seed)
    ifcopenshell.api.geometry.assign_representation(ifc_file, product=space, representation=seed_rep)

    local_shapes = _build_local_shapes(ifc_file)
    boundary_class = "IfcRelSpaceBoundary1stLevel"
    if ifc_file.schema == "IFC2X3":
        boundary_class = "IfcRelSpaceBoundary"
    boundaries = ifcopenshell.util.boundary.auto_generate_boundaries(
        ifc_file, space, local_shapes, boundary_class=boundary_class
    )
    if isinstance(boundaries, str) or not boundaries:
        ifcopenshell.api.geometry.remove_representation(ifc_file, representation=seed_rep)
        return None

    points = []
    point_index = {}
    faces = []

    def add_point(p):
        key = tuple(np.round(p, 5))
        if key not in point_index:
            point_index[key] = len(points)
            points.append([float(c) for c in p])
        return point_index[key]

    for boundary in boundaries:
        connection = boundary.ConnectionGeometry
        if connection is None:
            continue
        surface = connection.SurfaceOnRelatingElement
        if surface is None or not surface.is_a("IfcCurveBoundedPlane"):
            continue
        outer = surface.OuterBoundary
        if outer is None or not outer.is_a("IfcPolyline"):
            continue
        matrix = ifcopenshell.util.placement.get_axis2placement(surface.BasisSurface.Position)
        poly_points = []
        for loop_point in outer.Points:
            local = np.array([float(c) for c in loop_point.Coordinates])
            if len(local) == 2:
                local = np.array([*local, 0.0])
            world = np.delete(matrix @ np.array([*local, 1.0]), 3)
            poly_points.append(world)
        if len(poly_points) >= 3:
            faces.append([add_point(p) for p in poly_points])

    ifcopenshell.api.geometry.remove_representation(ifc_file, representation=seed_rep)

    if not faces:
        return None

    tri_faces = []
    for face in faces:
        for i in range(1, len(face) - 1):
            tri_faces.append([face[0], face[i], face[i + 1]])

    return builder.mesh(points, tri_faces)
