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

from typing import Optional, Union

import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.shape
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
