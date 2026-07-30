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

BOUNDARY_ELEMENT_CLASSES = ("IfcWall", "IfcColumn", "IfcSlab", "IfcVirtualElement", "IfcCurtainWall")


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

    # Don't generate boundaries for elements that already have boundaries
    for boundary in space.BoundedBy:
        if boundary.RelatedBuildingElement in building_elements:
            building_elements.remove(boundary.RelatedBuildingElement)

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

    # Compare space faces and building element faces
    for space_ngon in space_ngons:
        space_verts_l = space_verts_local[space_ngon]
        # Normal from local verts, then transform to world via space placement
        space_face_normal_local = _face_normal(space_verts_l)
        if space_face_normal_local is None:
            continue
        space_face_normal_world = space_matrix_3x3 @ space_face_normal_local

        for element in building_elements:
            element_shape = shapes[element.id()]
            element_matrix = element_shape["matrix"]
            element_matrix_3x3 = element_matrix[:3, :3]
            element_matrix_inv = np.linalg.inv(element_matrix)

            for ngon in element_ngons[element.id()]:
                elem_verts_l = element_shape["verts"][ngon]
                # Normal from local verts, transform to world via element placement
                elem_face_normal_local = _face_normal(elem_verts_l)
                if elem_face_normal_local is None:
                    continue
                elem_face_normal_world = element_matrix_3x3 @ elem_face_normal_local

                # Both normals point outward from their respective solids.
                # Adjacent faces have anti-parallel normals (angle ≈ 180°).
                # Virtual elements use parallel normals (angle ≈ 0°).
                angle = degrees(acos(max(min(float(np.dot(space_face_normal_world, elem_face_normal_world)), 1), -1)))
                if _is_x(angle, 180, tolerance=2):
                    pass
                elif element.is_a("IfcVirtualElement") and _is_x(angle, 0, tolerance=2):
                    pass
                else:
                    continue

                # Distance check: transform space vert to element-local, compare to element face
                # space-local -> world -> element-local
                space_vert_in_elem = sb.np_apply_matrix(space_verts_l[:1], element_matrix_inv @ space_matrix)[0]
                dist = float(np.dot(space_vert_in_elem - elem_verts_l[0], elem_face_normal_local))
                if abs(dist) > 0.05:
                    continue

                # Build face matrix in space-local coordinates
                # (assign_connection_geometry expects location/axes relative to space placement)
                face_matrix = _face_matrix_from_verts(space_verts_l[:3])
                face_matrix_inv = np.linalg.inv(face_matrix)

                # Project space face (already space-local) to 2D
                space_face_polygon = _verts_to_polygon(space_verts_l, face_matrix_inv)
                if not space_face_polygon.is_valid:
                    space_face_polygon = space_face_polygon.buffer(0)

                # Transform element verts to space-local, then project to 2D
                # element-local -> world -> space-local
                elem_verts_in_space = sb.np_apply_matrix(elem_verts_l, space_matrix_inv @ element_matrix)
                face_polygon = _verts_to_polygon(elem_verts_in_space, face_matrix_inv)
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

                if type(gross_boundary_polygon) == shapely.GeometryCollection:
                    for geom in gross_boundary_polygon.geoms:
                        if type(geom) == shapely.Polygon:
                            gross_boundary_polygon = geom
                            break

                if not (isinstance(gross_boundary_polygon, shapely.Polygon) and gross_boundary_polygon.is_valid):
                    continue
                if gross_boundary_polygon.is_empty:
                    continue

                exterior_boundary_polygon = shapely.Polygon(gross_boundary_polygon.exterior.coords)

                # Create parent boundary
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

                # Process openings
                boundaries.extend(
                    _process_openings(
                        ifc_file,
                        element,
                        elem_face_normal_world,
                        space_matrix_inv,
                        element_matrix,
                        face_matrix,
                        face_matrix_inv,
                        exterior_boundary_polygon,
                        boundary_class,
                        parent_boundary,
                        space,
                        unit_scale,
                    )
                )

    return boundaries


def _process_openings(
    ifc_file,
    building_element,
    face_normal_world,
    space_matrix_inv,
    element_matrix,
    face_matrix,
    face_matrix_inv,
    exterior_boundary_polygon,
    boundary_class,
    parent_boundary,
    space,
    unit_scale,
):
    """Process openings and fillings for a building element.

    :param face_normal_world: The building element face normal in world space.
    :param space_matrix_inv: Inverse of the space placement matrix.
    :param element_matrix: The building element placement matrix.
    :param face_matrix: The face matrix in space-local coordinates (for connection geometry).
    :param face_matrix_inv: The inverse face matrix (for 2D projection).
    """
    boundaries = []

    for rel in getattr(building_element, "HasOpenings", []):
        opening = rel.RelatedOpeningElement
        filling = opening.HasFillings[0].RelatedBuildingElement if opening.HasFillings else None

        settings = ifcopenshell.geom.settings()
        try:
            shape = ifcopenshell.geom.create_shape(settings, opening)
        except Exception:
            continue
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
            # Normal from local verts, transform to world via opening placement
            o_normal_local = _face_normal(o_verts_l)
            if o_normal_local is None:
                continue
            o_normal_world = opening_matrix_3x3 @ o_normal_local
            angle = degrees(acos(max(min(float(np.dot(o_normal_world, face_normal_world)), 1), -1)))
            if not _is_x(angle, 180, tolerance=2):
                continue
            # Transform opening verts to space-local: opening-local -> world -> space-local
            o_verts_in_space = sb.np_apply_matrix(o_verts_l, space_matrix_inv @ opening_matrix)
            polygon = _verts_to_polygon(o_verts_in_space, face_matrix_inv)
            opening_polygons.append(polygon)

        if not opening_polygons:
            continue

        opening_polygon = shapely.ops.unary_union(opening_polygons)

        if opening_polygon.intersection(exterior_boundary_polygon).area == 0:
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
        boundaries.append(boundary)

    return boundaries


def _face_normal(verts: np.ndarray) -> Optional[np.ndarray]:
    """Compute the normal of a polygon from its vertices."""
    if len(verts) < 3:
        return None
    return sb.np_normal([verts[0], verts[1], verts[2]])


def _face_matrix_from_verts(verts3: np.ndarray) -> np.ndarray:
    """Build a 4x4 face-local coordinate matrix from 3 vertices."""
    p1, p2, p3 = verts3[0], verts3[1], verts3[2]
    z = sb.np_normal([p1, p2, p3])
    x = sb.np_normalized(p2 - p1)
    return ifcopenshell.util.placement.a2p(o=p1, z=z, x=x)


def _verts_to_polygon(verts: np.ndarray, face_matrix_inv: np.ndarray) -> shapely.Polygon:
    """Project 3D vertices onto a 2D plane and create a shapely Polygon."""
    verts_2d = sb.np_apply_matrix(verts, face_matrix_inv)[:, :2]
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


def _is_x(value: float, x: float, tolerance: float = 1e-5) -> bool:
    """Check whether value is within tolerance of x."""
    return (x + tolerance) > value > (x - tolerance)
