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

"""Blender-independent IfcRelSpaceBoundary generation from IFC geometry.

These functions operate on IFC geometry data (vertices, faces, edges,
element relationships) without requiring any Blender objects to be loaded.
"""

from __future__ import annotations

import logging
from math import acos, degrees
from typing import Optional, Union

import ifcopenshell
import ifcopenshell.api.boundary
import ifcopenshell.api.root
import ifcopenshell.geom
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.shape
import ifcopenshell.util.shape_builder as sb
import ifcopenshell.util.unit
import numpy as np
import shapely
import shapely.ops

logger = logging.getLogger("ImportIFC")

BOUNDARY_ELEMENT_CLASSES = (
    "IfcWall",
    "IfcColumn",
    "IfcSlab",
    "IfcRoof",
    "IfcVirtualElement",
    "IfcCurtainWall",
    "IfcWindow",
    "IfcDoor",
)

# Plane offset (in meters) below which a sole bounding element is assigned the
# full space face. Building element faces are often slightly offset from the
# space face they bound (e.g. wall linings), so a single bounding element
# within this offset gets the complete face rather than a clipped polygon.
FULL_FACE_OFFSET_TOL = 0.25


def _union_coplanar_face_polygon(
    space_verts_local,
    space_triangles,
    face_origin,
    face_normal,
    face_matrix_inv,
    fallback,
):
    """Reconstruct a space face from its raw triangles.

    ``dissolve_faces`` with ``merge_coplanar=True`` drops any interior rings
    (holes) when coplanar faces are merged, e.g. a ceiling pierced by a shaft
    or an opening. Unioning the raw triangles coplanar with the face restores
    those holes.
    """
    polygons = []
    for triangle in space_triangles:
        points = space_verts_local[triangle]
        if _face_normal(points) is None:
            continue
        if np.abs(np.dot(points - face_origin, face_normal)).max() > 1e-4:
            continue
        polygon = _verts_to_polygon(points, face_matrix_inv, snap=1e-6)
        if not polygon.is_valid:
            polygon = polygon.buffer(0)
        if polygon.is_empty:
            continue
        polygons.append(polygon)
    if not polygons:
        return fallback
    union = shapely.ops.unary_union(polygons).buffer(0)
    if isinstance(union, shapely.Polygon):
        return union
    if isinstance(union, shapely.MultiPolygon):
        best, best_area = None, -1.0
        for polygon in union.geoms:
            overlap = polygon.intersection(fallback).area
            if overlap > best_area:
                best, best_area = polygon, overlap
        return best if best is not None else fallback
    return fallback


def auto_generate_boundaries(
    ifc_file: ifcopenshell.file,
    space: ifcopenshell.entity_instance,
    shapes: dict,
    boundary_class: str,
    boundary_element_classes: tuple = BOUNDARY_ELEMENT_CLASSES,
) -> Union[str, list[ifcopenshell.entity_instance]]:
    """Generate IfcRelSpaceBoundary records from IFC geometry without Blender.

    :param ifc_file: The IFC file.
    :param space: The IfcSpace entity to generate boundaries for.
    :param shapes: Dict ``{element_id: {"verts": ndarray, "faces": ndarray,
        "edges": ndarray, "matrix": ndarray}}``. Must include the space itself.
        Built by the caller via ``ifcopenshell.geom.iterator``.
    :param boundary_class: IFC class for boundaries (e.g.
        ``"IfcRelSpaceBoundary2ndLevel"``).
    :param boundary_element_classes: IFC classes to consider as boundary elements.
    :return: List of created ``IfcRelSpaceBoundary`` entities, or error string.
    """
    boundaries: list[ifcopenshell.entity_instance] = []

    space_shape = shapes.get(space.id())
    if space_shape is None:
        return "Space geometry not found in shapes dict."

    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(ifc_file)

    # Identify all potential building elements
    building_elements = []
    for ifc_class in boundary_element_classes:
        building_elements.extend(ifc_file.by_type(ifc_class))

    # Delete existing boundaries so they are regenerated. remove_deep2 cannot be
    # used on the boundary itself because 2nd level boundaries are referenced via
    # their ParentBoundary and CorrelationId attributes by other boundaries.
    for boundary in list(space.BoundedBy or []):
        if boundary.RelatedBuildingElement in building_elements:
            ifcopenshell.api.boundary.remove_boundary(ifc_file, boundary)

    # Filter to elements that have shapes in the cache
    building_elements = [e for e in building_elements if e.id() in shapes]

    if not building_elements:
        return "No building elements found to create boundaries."

    # Dissolve space mesh — verts are in local coords, matrix is the placement
    space_matrix = space_shape["matrix"]
    space_matrix_3x3 = space_matrix[:3, :3]
    space_matrix_inv = np.linalg.inv(space_matrix)
    # Space verts are already local (get_vertices without use-world-coords)
    space_verts_local = space_shape["verts"]
    space_ngons = ifcopenshell.util.shape.dissolve_faces(
        space_verts_local, space_shape["faces"], space_shape["edges"], merge_coplanar=True
    )

    # Dissolve building element meshes — verts are in element-local coords
    element_ngons = {}
    for element in building_elements:
        es = shapes[element.id()]
        element_ngons[element.id()] = ifcopenshell.util.shape.dissolve_faces(
            es["verts"], es["faces"], es["edges"], merge_coplanar=True
        )

    # Separate from processed_fillings (used by _process_openings) so that
    # pre-populating does not cause _process_openings to skip fillings.
    all_filling_ids: set[int] = set()
    for element in building_elements:
        for rel in getattr(element, "HasOpenings", []):
            if not (opening := rel.RelatedOpeningElement).HasFillings:
                continue
            for fills_rel in opening.HasFillings:
                all_filling_ids.add(fills_rel.RelatedBuildingElement.id())

    # Some models have openings without an IfcRelFillsElement relation (e.g. a
    # window placed directly on top of an opening in a roof). Detect these
    # fillings geometrically by matching the projected footprint of a window or
    # door with the opening it occupies.
    geometric_fillings: dict[int, ifcopenshell.entity_instance] = {}
    filling_candidates = []
    for element in building_elements:
        if element.is_a() not in ("IfcWindow", "IfcDoor") or element.id() in all_filling_ids:
            continue
        es = shapes[element.id()]
        world = sb.np_apply_matrix(es["verts"], es["matrix"])
        filling_candidates.append(
            (
                element,
                shapely.box(world[:, 0].min(), world[:, 1].min(), world[:, 0].max(), world[:, 1].max()),
                float(world[:, 2].min()),
                float(world[:, 2].max()),
            )
        )

    if filling_candidates:
        settings = ifcopenshell.geom.settings()
        for element in building_elements:
            for rel in getattr(element, "HasOpenings", []):
                opening = rel.RelatedOpeningElement
                if opening.HasFillings:
                    continue
                try:
                    o_shape = ifcopenshell.geom.create_shape(settings, opening)
                except Exception:
                    continue
                o_verts = ifcopenshell.util.shape.get_vertices(o_shape.geometry)
                o_matrix = ifcopenshell.util.shape.get_shape_matrix(o_shape)
                o_world = sb.np_apply_matrix(o_verts, o_matrix)
                o_xy_box = shapely.box(
                    o_world[:, 0].min(), o_world[:, 1].min(), o_world[:, 0].max(), o_world[:, 1].max()
                )
                o_zmin, o_zmax = float(o_world[:, 2].min()), float(o_world[:, 2].max())
                best_filling = None
                best_overlap = 0.0
                for candidate, c_xy_box, c_zmin, c_zmax in filling_candidates:
                    overlap = o_xy_box.intersection(c_xy_box).area
                    if overlap < 0.8 * min(o_xy_box.area, c_xy_box.area):
                        continue
                    if max(o_zmin, c_zmin) - min(o_zmax, c_zmax) > 0.1:
                        continue
                    if overlap > best_overlap:
                        best_overlap = overlap
                        best_filling = candidate
                if best_filling is not None:
                    geometric_fillings[opening.id()] = best_filling
                    all_filling_ids.add(best_filling.id())

    processed_fillings: set[int] = set()
    matched_element_ids: set[int] = set()
    matched_walls_and_columns: set[int] = set()

    space_centroid_world = sb.np_apply_matrix(np.mean(space_verts_local, axis=0)[np.newaxis], space_matrix)[0]

    # Per-face data used to detect and fill gaps so that generated boundaries
    # form a water-tight enclosure.
    space_face_polygons = {}
    face_matrices = {}
    face_matrix_invs = {}
    space_face_normals_world = {}
    covered_by_face = {}

    for space_ngon_idx, space_ngon in enumerate(space_ngons):
        space_verts_l = space_verts_local[space_ngon]
        space_face_normal_local = _face_normal(space_verts_l)
        if space_face_normal_local is None:
            continue
        space_face_normal_local = _ensure_outward(
            space_face_normal_local, space_verts_l, space_centroid_world, space_matrix
        )
        space_face_normal_world = space_matrix_3x3 @ space_face_normal_local

        face_matrix = _face_matrix_from_verts(space_verts_l[:3])
        face_matrix_inv = np.linalg.inv(face_matrix)
        space_face_polygon = _verts_to_polygon(space_verts_l, face_matrix_inv, snap=1e-6)
        if not space_face_polygon.is_valid:
            space_face_polygon = space_face_polygon.buffer(0)
        space_face_polygon = _union_coplanar_face_polygon(
            space_verts_local,
            space_shape["faces"],
            space_verts_l[0],
            space_face_normal_local,
            face_matrix_inv,
            space_face_polygon,
        )
        space_face_polygons[space_ngon_idx] = space_face_polygon
        face_matrices[space_ngon_idx] = face_matrix
        face_matrix_invs[space_ngon_idx] = face_matrix_inv
        space_face_normals_world[space_ngon_idx] = space_face_normal_world
        covered_by_face[space_ngon_idx] = []

        candidates = []
        for element in building_elements:
            if element.id() in all_filling_ids:
                continue
            if element.is_a() in ("IfcWall", "IfcColumn") and element.id() in matched_walls_and_columns:
                continue
            match = _match_element_to_space_face(
                element,
                shapes,
                element_ngons,
                space_matrix,
                space_matrix_inv,
                space_verts_l,
                space_face_polygon,
                face_matrix_inv,
                space_face_normal_world,
            )
            if match is None:
                continue
            dist_min, plane_offset_min, matching_polygons, matched_elem_normal = match

            if len(matching_polygons) == 1:
                gross_boundary_polygon = matching_polygons[0]
            else:
                gross_boundary_polygon = shapely.ops.unary_union(matching_polygons)
                if type(gross_boundary_polygon) == shapely.GeometryCollection:
                    for geom in gross_boundary_polygon.geoms:
                        if type(geom) == shapely.Polygon:
                            gross_boundary_polygon = geom
                            break

            if not (isinstance(gross_boundary_polygon, shapely.Polygon) and gross_boundary_polygon.is_valid):
                continue
            if gross_boundary_polygon.is_empty:
                continue

            candidates.append((element, dist_min, plane_offset_min, gross_boundary_polygon, matched_elem_normal))

        # A space face may be matched by several elements within the distance
        # tolerance (e.g. a second wall layer or an element end cap). The
        # element closest to the face is the actual bounding surface, so
        # candidates are kept in order of increasing plane offset (ties broken
        # by polygon area). A candidate whose polygon is entirely covered by
        # the candidates already kept is redundant and is absorbed into the
        # larger boundary.
        surviving_candidates = []
        kept_union = None
        for element, dist_min, plane_offset_min, gross_boundary_polygon, matched_elem_normal in sorted(
            candidates, key=lambda c: (c[2] if c[2] is not None else float("inf"), -c[3].area)
        ):
            if kept_union is not None and gross_boundary_polygon.difference(kept_union).area < 1e-4:
                continue
            surviving_candidates.append(
                (element, dist_min, plane_offset_min, gross_boundary_polygon, matched_elem_normal)
            )
            kept_union = gross_boundary_polygon if kept_union is None else kept_union.union(gross_boundary_polygon)

        # When a single element bounds the space face and its face is (nearly)
        # coplanar with it, the boundary covers the full space face (1st level
        # semantics) rather than the clipped intersection with the element
        # face. This matches the reference output and avoids leaving corner
        # slivers to be filled by an extra gap boundary.
        if len(surviving_candidates) == 1:
            element, dist_min, plane_offset_min, gross_boundary_polygon, matched_elem_normal = surviving_candidates[0]
            if plane_offset_min is not None and plane_offset_min <= FULL_FACE_OFFSET_TOL:
                gross_boundary_polygon = space_face_polygon
            surviving_candidates[0] = (element, dist_min, plane_offset_min, gross_boundary_polygon, matched_elem_normal)

        for element, dist_min, plane_offset_min, gross_boundary_polygon, matched_elem_normal in surviving_candidates:
            exterior_boundary_polygon = gross_boundary_polygon

            opening_source_element = element
            for rel in getattr(element, "Decomposes", []):
                if rel.RelatingObject.is_a() in BOUNDARY_ELEMENT_CLASSES:
                    element = rel.RelatingObject
                    break

            # The gross boundary polygon may still carry the openings of the
            # building element (e.g. when the authoring tool baked them into the
            # element geometry). An inner boundary is supposed to overlap its
            # parent boundary according to IFC4 documentation, so the openings
            # are unioned back into the parent to keep it hole-free while the
            # filling gets its own parented boundary.
            openings_to_process = []
            for rel in getattr(opening_source_element, "HasOpenings", []):
                opening = rel.RelatedOpeningElement
                filling = (
                    opening.HasFillings[0].RelatedBuildingElement
                    if opening.HasFillings
                    else geometric_fillings.get(opening.id())
                )
                if filling is None:
                    continue
                opening_polygon = _compute_opening_polygon(
                    ifc_file, opening, matched_elem_normal, space_matrix_inv, face_matrix_inv
                )
                if opening_polygon is None:
                    continue
                if opening_polygon.intersection(gross_boundary_polygon).area == 0:
                    continue
                openings_to_process.append((opening, filling, opening_polygon))

            exterior_boundary_polygon = _union_openings_into_parent(exterior_boundary_polygon, openings_to_process)

            exterior_boundary_polygon = exterior_boundary_polygon.simplify(1e-5)
            if isinstance(exterior_boundary_polygon, shapely.Polygon) and not exterior_boundary_polygon.is_empty:
                ext_coords = [
                    (round(x / 1e-8) * 1e-8, round(y / 1e-8) * 1e-8)
                    for x, y in exterior_boundary_polygon.exterior.coords
                ]
                int_coords = [
                    [(round(x / 1e-8) * 1e-8, round(y / 1e-8) * 1e-8) for x, y in interior.coords]
                    for interior in exterior_boundary_polygon.interiors
                ]
                snapped = shapely.Polygon(ext_coords, int_coords)
                if not snapped.is_empty:
                    cleaned = snapped.buffer(0).simplify(1e-5)
                    if isinstance(cleaned, shapely.Polygon) and not cleaned.is_empty:
                        exterior_boundary_polygon = cleaned

            matched_walls_and_columns.add(element.id())

            parent_boundary = ifcopenshell.api.root.create_entity(ifc_file, ifc_class=boundary_class)
            if element.is_a("IfcVirtualElement"):
                parent_boundary.PhysicalOrVirtualBoundary = "VIRTUAL"
            else:
                parent_boundary.PhysicalOrVirtualBoundary = "PHYSICAL"
            parent_boundary.InternalOrExternalBoundary = "NOTDEFINED"
            _set_internal_external(parent_boundary, element)
            parent_boundary.RelatingSpace = space
            parent_boundary.RelatedBuildingElement = element

            _assign_connection_geometry(
                ifc_file,
                parent_boundary,
                exterior_boundary_polygon,
                face_matrix,
                unit_scale,
            )
            _set_boundary_name(parent_boundary)
            boundaries.append(parent_boundary)
            covered_by_face[space_ngon_idx].append(exterior_boundary_polygon)

            boundaries.extend(
                _process_openings(
                    ifc_file,
                    openings_to_process,
                    face_matrix,
                    boundary_class,
                    parent_boundary,
                    space,
                    unit_scale,
                    processed_fillings,
                    covered_by_face[space_ngon_idx],
                )
            )

    boundaries.extend(
        _fill_face_gaps(
            ifc_file,
            space,
            boundary_class,
            unit_scale,
            space_face_polygons,
            face_matrices,
            face_matrix_invs,
            space_face_normals_world,
            space_verts_local,
            space_ngons,
            space_matrix,
            space_matrix_inv,
            shapes,
            element_ngons,
            covered_by_face,
            building_elements,
            all_filling_ids,
            matched_walls_and_columns,
        )
    )

    return boundaries


def _match_element_to_space_face(
    element,
    shapes,
    element_ngons,
    space_matrix,
    space_matrix_inv,
    space_verts_l,
    space_face_polygon,
    face_matrix_inv,
    space_face_normal_world,
):
    """Match a building element's faces against a single space face.

    :return: A tuple ``(dist_min, matching_polygons, matched_elem_normal)`` with
        the minimum face distance, the matching boundary polygons and the matched
        face normal in world space, or ``None`` when the element does not bound
        this space face.
    """
    element_shape = shapes[element.id()]
    element_matrix = element_shape["matrix"]
    element_matrix_3x3 = element_matrix[:3, :3]
    element_matrix_inv = np.linalg.inv(element_matrix)

    element_centroid_world = sb.np_apply_matrix(np.mean(element_shape["verts"], axis=0)[np.newaxis], element_matrix)[0]

    space_centroid = np.mean(space_verts_l, axis=0)

    matching_polygons = []
    matched_elem_normal = None
    dist_min = None
    plane_offset_min = None

    for ngon in element_ngons[element.id()]:
        elem_verts_l = element_shape["verts"][ngon]
        elem_face_normal_local = _face_normal(elem_verts_l)
        if elem_face_normal_local is None:
            continue
        elem_face_normal_local = _ensure_outward(
            elem_face_normal_local, elem_verts_l, element_centroid_world, element_matrix
        )
        elem_face_normal_world = element_matrix_3x3 @ elem_face_normal_local

        angle = degrees(acos(max(min(float(np.dot(space_face_normal_world, elem_face_normal_world)), 1), -1)))
        is_horizontal_face = abs(space_face_normal_world[2]) > 0.5 and abs(elem_face_normal_world[2]) > 0.5
        is_valid_element = (
            element.is_a("IfcVirtualElement")
            or element.is_a("IfcSlab")
            or element.is_a("IfcWindow")
            or element.is_a("IfcDoor")
        )
        is_anti_parallel = _is_x(angle, 180, tolerance=2)
        is_parallel = _is_x(angle, 0, tolerance=2)

        if not (is_anti_parallel or (is_horizontal_face and is_parallel and is_valid_element)):
            continue

        sv_in_elem = sb.np_apply_matrix(space_centroid[np.newaxis], element_matrix_inv @ space_matrix)[0]
        dist = float(np.dot(sv_in_elem - elem_verts_l[0], elem_face_normal_local))
        dist_tol = 0.05 if is_horizontal_face else 0.5
        if abs(dist) > dist_tol:
            continue

        elem_verts_in_space = sb.np_apply_matrix(elem_verts_l, space_matrix_inv @ element_matrix)
        face_polygon = _verts_to_polygon(elem_verts_in_space, face_matrix_inv, snap=1e-6)
        if not face_polygon.is_valid:
            face_polygon = face_polygon.buffer(0)

        try:
            gross_boundary_polygon = space_face_polygon.intersection(face_polygon)
        except shapely.errors.GEOSException:
            logger.warning(
                "Skipping invalid geometry for %s (shapely topology error).",
                element.Name or element.is_a(),
                exc_info=True,
            )
            continue

        if gross_boundary_polygon.is_empty or gross_boundary_polygon.area < 1e-4:
            continue

        if type(gross_boundary_polygon) == shapely.GeometryCollection:
            for geom in gross_boundary_polygon.geoms:
                if type(geom) == shapely.Polygon:
                    gross_boundary_polygon = geom
                    break

        if not (isinstance(gross_boundary_polygon, shapely.Polygon) and gross_boundary_polygon.is_valid):
            continue
        if gross_boundary_polygon.is_empty:
            continue

        matching_polygons.append(gross_boundary_polygon)
        matched_elem_normal = elem_face_normal_world
        dist_min = abs(dist) if dist_min is None else min(dist_min, abs(dist))
        space_face_normal = _face_normal(space_verts_l)
        if space_face_normal is not None:
            plane_offset = abs(float(np.dot(space_face_normal, elem_verts_in_space[0] - space_verts_l[0])))
            plane_offset_min = plane_offset if plane_offset_min is None else min(plane_offset_min, plane_offset)

    if not matching_polygons:
        return None
    return dist_min, plane_offset_min, matching_polygons, matched_elem_normal


def _union_openings_into_parent(exterior_boundary_polygon, openings_to_process):
    """Union the opening polygons back into the parent boundary polygon.

    Authoring tools may bake openings into the building element mesh, so the
    parent boundary polygon can be notched where the opening is. Since an inner
    boundary is supposed to overlap its parent boundary, the openings are
    unioned back into the parent while the filling gets its own boundary.
    """
    for _, _, opening_polygon in openings_to_process:
        unionised_object = exterior_boundary_polygon.union(opening_polygon)
        if isinstance(unionised_object, shapely.Polygon):
            exterior_boundary_polygon = unionised_object
    return exterior_boundary_polygon


def _compute_opening_polygon(ifc_file, opening, face_normal_world, space_matrix_inv, face_matrix_inv):
    """Project an opening onto the building element face in space-local coordinates.

    :param opening: The IfcOpeningElement to project.
    :param face_normal_world: The building element face normal in world space.
    :param space_matrix_inv: Inverse of the space placement matrix.
    :param face_matrix_inv: The inverse face matrix (for 2D projection).
    :return: A 2D shapely polygon in space-local coordinates, or None.
    """
    settings = ifcopenshell.geom.settings()
    try:
        shape = ifcopenshell.geom.create_shape(settings, opening)
    except Exception:
        return None
    opening_verts_l = ifcopenshell.util.shape.get_vertices(shape.geometry)
    opening_faces = ifcopenshell.util.shape.get_faces(shape.geometry)
    opening_edges = ifcopenshell.util.shape.get_edges(shape.geometry)
    opening_matrix = ifcopenshell.util.shape.get_shape_matrix(shape)
    opening_matrix_3x3 = opening_matrix[:3, :3]

    opening_ngons = ifcopenshell.util.shape.dissolve_faces(
        opening_verts_l, opening_faces, opening_edges, merge_coplanar=True
    )

    opening_polygons = []
    for ngon in opening_ngons:
        o_verts_l = opening_verts_l[ngon]
        o_normal_local = _face_normal(o_verts_l)
        if o_normal_local is None:
            continue
        o_normal_world = opening_matrix_3x3 @ o_normal_local
        angle = degrees(acos(max(min(float(np.dot(o_normal_world, face_normal_world)), 1), -1)))
        if not _is_x(angle, 180, tolerance=2):
            continue
        o_verts_in_space = sb.np_apply_matrix(o_verts_l, space_matrix_inv @ opening_matrix)
        polygon = _verts_to_polygon(o_verts_in_space, face_matrix_inv)
        opening_polygons.append(polygon)

    if not opening_polygons:
        return None

    return shapely.ops.unary_union(opening_polygons)


def _process_openings(
    ifc_file,
    openings_to_process,
    face_matrix,
    boundary_class,
    parent_boundary,
    space,
    unit_scale,
    processed_fillings: set[int],
    covered_polygons: list,
):
    """Create boundaries for the fillings of openings in a building element.

    :param openings_to_process: Tuples of (opening, filling, opening polygon).
    :param face_matrix: The face matrix in space-local coordinates (for connection geometry).
    :param processed_fillings: Set of element IDs that already have opening boundaries.
    :param covered_polygons: Accumulated boundary polygons used for water-tightness checks.
    """
    boundaries = []

    for opening, filling, opening_polygon in openings_to_process:
        filling_id = filling.id()
        if filling_id in processed_fillings:
            continue

        boundary = ifcopenshell.api.root.create_entity(ifc_file, ifc_class=boundary_class)
        boundary.RelatingSpace = space
        boundary.RelatedBuildingElement = filling or opening

        # Use the same space-local face_matrix for connection geometry
        _assign_connection_geometry(
            ifc_file,
            boundary,
            opening_polygon,
            face_matrix,
            unit_scale,
        )
        if filling:
            boundary.PhysicalOrVirtualBoundary = "PHYSICAL"
        else:
            boundary.PhysicalOrVirtualBoundary = "VIRTUAL"
        boundary.InternalOrExternalBoundary = parent_boundary.InternalOrExternalBoundary
        if boundary.is_a() != "IfcRelSpaceBoundary":
            boundary.ParentBoundary = parent_boundary
        _set_boundary_name(boundary)
        processed_fillings.add(filling_id)
        covered_polygons.append(opening_polygon)
        boundaries.append(boundary)

    return boundaries


def _fill_face_gaps(
    ifc_file,
    space,
    boundary_class,
    unit_scale,
    space_face_polygons,
    face_matrices,
    face_matrix_invs,
    space_face_normals_world,
    space_verts_local,
    space_ngons,
    space_matrix,
    space_matrix_inv,
    shapes,
    element_ngons,
    covered_by_face,
    building_elements,
    all_filling_ids,
    matched_walls_and_columns,
):
    """Create boundaries for uncovered parts of space faces to keep them water tight."""
    boundaries = []
    for face_idx, space_face_polygon in space_face_polygons.items():
        covered_polygons = covered_by_face.get(face_idx, [])
        if not covered_polygons:
            continue
        uncovered = space_face_polygon.difference(shapely.ops.unary_union(covered_polygons))
        if uncovered.is_empty:
            continue
        if isinstance(uncovered, shapely.Polygon):
            fragments = [uncovered]
        elif isinstance(uncovered, shapely.MultiPolygon):
            fragments = list(uncovered.geoms)
        else:
            continue
        for fragment in fragments:
            if fragment.area < 1e-2:
                continue
            element = _best_element_for_gap(
                fragment,
                space_verts_local[space_ngons[face_idx]],
                space_matrix,
                space_matrix_inv,
                face_matrices[face_idx],
                face_matrix_invs[face_idx],
                space_face_normals_world[face_idx],
                shapes,
                element_ngons,
                building_elements,
                all_filling_ids,
                matched_walls_and_columns,
            )
            if element is None:
                logger.warning(
                    "No element found to fill a gap on a face of space %s.",
                    space.Name or space.is_a(),
                )
                continue
            parent_boundary = ifcopenshell.api.root.create_entity(ifc_file, ifc_class=boundary_class)
            parent_boundary.PhysicalOrVirtualBoundary = "PHYSICAL"
            parent_boundary.InternalOrExternalBoundary = "NOTDEFINED"
            _set_internal_external(parent_boundary, element)
            parent_boundary.RelatingSpace = space
            parent_boundary.RelatedBuildingElement = element
            _assign_connection_geometry(
                ifc_file,
                parent_boundary,
                fragment,
                face_matrices[face_idx],
                unit_scale,
            )
            _set_boundary_name(parent_boundary)
            boundaries.append(parent_boundary)
    return boundaries


def _best_element_for_gap(
    fragment,
    space_face_verts,
    space_matrix,
    space_matrix_inv,
    face_matrix,
    face_matrix_inv,
    space_face_normal_world,
    shapes,
    element_ngons,
    building_elements,
    all_filling_ids,
    matched_walls_and_columns,
):
    """Find the element most appropriate to cover an uncovered part of a space face."""
    best = None
    best_overlap = 0.0
    space_centroid = np.mean(space_face_verts, axis=0)

    for element in building_elements:
        if element.id() in all_filling_ids:
            continue
        # Walls and columns already bounding this space keep a single boundary;
        # a gap is therefore filled by a neighbouring element instead.
        if element.is_a() in ("IfcWall", "IfcColumn") and element.id() in matched_walls_and_columns:
            continue
        es = shapes[element.id()]
        e_matrix = es["matrix"]
        e_matrix_3x3 = e_matrix[:3, :3]
        e_matrix_inv = np.linalg.inv(e_matrix)
        e_centroid_world = sb.np_apply_matrix(np.mean(es["verts"], axis=0)[np.newaxis], e_matrix)[0]

        for ngon in element_ngons[element.id()]:
            elem_verts_l = es["verts"][ngon]
            normal_local = _face_normal(elem_verts_l)
            if normal_local is None:
                continue
            normal_local = _ensure_outward(normal_local, elem_verts_l, e_centroid_world, e_matrix)
            normal_world = e_matrix_3x3 @ normal_local
            angle = degrees(acos(max(min(float(np.dot(space_face_normal_world, normal_world)), 1), -1)))
            is_horizontal_face = abs(space_face_normal_world[2]) > 0.5 and abs(normal_world[2]) > 0.5
            is_valid_element = (
                element.is_a("IfcVirtualElement")
                or element.is_a("IfcSlab")
                or element.is_a("IfcWindow")
                or element.is_a("IfcDoor")
            )
            if not (
                _is_x(angle, 180, tolerance=2)
                or (is_horizontal_face and _is_x(angle, 0, tolerance=2) and is_valid_element)
            ):
                continue
            sv_in_elem = sb.np_apply_matrix(space_centroid[np.newaxis], e_matrix_inv @ space_matrix)[0]
            dist = float(np.dot(sv_in_elem - elem_verts_l[0], normal_local))
            dist_tol = 0.05 if is_horizontal_face else 0.5
            if abs(dist) > dist_tol:
                continue
            elem_verts_in_space = sb.np_apply_matrix(elem_verts_l, space_matrix_inv @ e_matrix)
            face_polygon = _verts_to_polygon(elem_verts_in_space, face_matrix_inv, snap=1e-6)
            if not face_polygon.is_valid:
                face_polygon = face_polygon.buffer(0)
            overlap = fragment.intersection(face_polygon).area
            if overlap > best_overlap:
                best_overlap = overlap
                best = element

    if best is not None:
        return best

    # For gaps at corners between non-parallel faces, fall back to the element
    # whose plan footprint covers the gap centroid.
    frag_2d = np.array([[c[0], c[1], 0.0] for c in fragment.exterior.coords])
    frag_local = sb.np_apply_matrix(frag_2d, face_matrix)
    frag_world = sb.np_apply_matrix(frag_local, space_matrix)
    frag_centroid = frag_world.mean(axis=0)
    is_horizontal_face = abs(space_face_normal_world[2]) > 0.5
    best = None
    best_dist = np.inf
    for element in building_elements:
        if element.id() in all_filling_ids:
            continue
        if is_horizontal_face:
            if not (element.is_a("IfcSlab") or element.is_a("IfcRoof") or element.is_a("IfcVirtualElement")):
                continue
        elif not (element.is_a("IfcWall") or element.is_a("IfcColumn") or element.is_a("IfcVirtualElement")):
            continue
        es = shapes[element.id()]
        world = sb.np_apply_matrix(es["verts"], es["matrix"])
        elem_xy = shapely.box(world[:, 0].min(), world[:, 1].min(), world[:, 0].max(), world[:, 1].max())
        if not elem_xy.contains(shapely.Point(frag_centroid[:2])):
            continue
        elem_centroid = world.mean(axis=0)
        dist = float(np.linalg.norm(elem_centroid - frag_centroid))
        if dist < best_dist:
            best_dist = dist
            best = element
    return best


def _face_normal(verts: np.ndarray) -> Optional[np.ndarray]:
    """Compute the normal of a polygon from its vertices."""
    if len(verts) < 3:
        return None
    for i in range(len(verts) - 2):
        v0, v1, v2 = verts[i], verts[i + 1], verts[i + 2]
        cross = np.cross(v1 - v0, v2 - v0)
        norm = np.linalg.norm(cross)
        if norm > 1e-8:
            return cross / norm
    return None


def _face_matrix_from_verts(verts3: np.ndarray) -> np.ndarray:
    """Build a 4x4 face-local coordinate matrix from 3 vertices."""
    p1, p2, p3 = verts3[0], verts3[1], verts3[2]
    z = sb.np_normal([p1, p2, p3])
    x = sb.np_normalized(p2 - p1)
    return ifcopenshell.util.placement.a2p(o=p1, z=z, x=x)


def _verts_to_polygon(verts: np.ndarray, face_matrix_inv: np.ndarray, snap: float = 0) -> shapely.Polygon:
    """Project 3D vertices onto a 2D plane and create a shapely Polygon."""
    verts_2d = sb.np_apply_matrix(verts, face_matrix_inv)[:, :2]
    if snap:
        verts_2d = np.round(verts_2d / snap) * snap
    return shapely.Polygon([tuple(v) for v in verts_2d])


def _assign_connection_geometry(
    ifc_file: ifcopenshell.file,
    boundary: ifcopenshell.entity_instance,
    polygon: shapely.Polygon,
    face_matrix: np.ndarray,
    unit_scale: float,
) -> None:
    """Assign connection geometry to a boundary using the existing API."""
    location = face_matrix[:3, 3]
    axis = face_matrix[:3, 2]
    ref_direction = face_matrix[:3, 0]

    outer_boundary = [list(coord) for coord in polygon.exterior.coords[:-1]]
    inner_boundaries = [list(interior.coords[:-1]) for interior in polygon.interiors]

    ifcopenshell.api.boundary.assign_connection_geometry(
        ifc_file,
        rel_space_boundary=boundary,
        outer_boundary=outer_boundary,
        location=location.tolist(),
        axis=axis.tolist(),
        ref_direction=ref_direction.tolist(),
        inner_boundaries=inner_boundaries if inner_boundaries else None,
        unit_scale=unit_scale,
    )


def _set_internal_external(
    boundary: ifcopenshell.entity_instance, building_element: ifcopenshell.entity_instance
) -> None:
    """Set InternalOrExternalBoundary based on element type and psets."""
    if building_element.is_a("IfcWall"):
        is_external = ifcopenshell.util.element.get_pset(building_element, "Pset_WallCommon", "IsExternal")
        if is_external is True:
            boundary.InternalOrExternalBoundary = "EXTERNAL"
        elif is_external is False:
            boundary.InternalOrExternalBoundary = "INTERNAL"
    elif building_element.is_a("IfcSlab"):
        predefined_type = ifcopenshell.util.element.get_predefined_type(building_element)
        if predefined_type == "BASESLAB":
            boundary.InternalOrExternalBoundary = "EXTERNAL_EARTH"
        else:
            is_external = ifcopenshell.util.element.get_pset(building_element, "Pset_SlabCommon", "IsExternal")
            if is_external is True:
                boundary.InternalOrExternalBoundary = "EXTERNAL"
            elif is_external is False:
                boundary.InternalOrExternalBoundary = "INTERNAL"


def _set_boundary_name(boundary: ifcopenshell.entity_instance) -> None:
    """Set Name/Description per IFC4x3 convention."""
    if boundary.is_a("IfcRelSpaceBoundary2ndLevel"):
        boundary.Name = "2ndLevel"
        if boundary.CorrespondingBoundary:
            boundary.Description = "2a"
        else:
            boundary.Description = "2b"
    elif boundary.is_a("IfcRelSpaceBoundary1stLevel"):
        boundary.Name = "1stLevel"


def _ensure_outward(
    normal_local: np.ndarray,
    face_verts_l: np.ndarray,
    entity_centroid_world: np.ndarray,
    entity_matrix: np.ndarray,
) -> np.ndarray:
    """Flip face normal to point away from the entity centroid."""
    face_centroid_world = sb.np_apply_matrix(np.mean(face_verts_l, axis=0)[np.newaxis], entity_matrix)[0]
    normal_world = entity_matrix[:3, :3] @ normal_local
    if np.dot(face_centroid_world - entity_centroid_world, normal_world) < 0:
        return -normal_local
    return normal_local


def _is_x(value: float, x: float, tolerance: float = 1e-5) -> bool:
    """Check whether value is within tolerance of x."""
    return (x + tolerance) > value > (x - tolerance)
