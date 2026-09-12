# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2023 Dion Moult <dion@thinkmoult.com>
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

from __future__ import annotations

from math import cos, radians
from typing import TYPE_CHECKING, Literal, Optional, Union

import numpy as np
import numpy.typing as npt
import shapely
import shapely.ops

import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation

if TYPE_CHECKING:

    import ifcopenshell.ifcopenshell_wrapper as W
    from ifcopenshell.geom import ShapeElementType
    from ifcopenshell.util.shape_builder import VectorType

    AXIS_LITERAL = Literal["X", "Y", "Z"]

    VECTOR_3D = tuple[float, float, float]

# Used only for typing, but reused by `shape.py` users.
MatrixType = npt.NDArray[np.float64]
"""`npt.NDArray[np.float64]`"""

tol = 1e-6

# NOTE: See representation.h for W.triangulation buffer types.

# NOTE: For functions that return a single scalar ensure to use .item() to
# return the Python float instead of numpy float
# as it's less intrusive (doesn't promote numpy arrays on interactions),
# doesn't fail saving to IFC
# and precise enough anyway (internally Python floats are doubles).


def is_x(value: float, x: float, tolerance: Optional[float] = None) -> bool:
    """Checks whether a value is equivalent to X given a tolerance

    :param value: Input value
    :param x: The value to compare to
    :param tolerance: The tolerance to use. Defaults to 1e-6.
    :return: True or false
    """
    if tolerance is None:
        tolerance = tol
    return abs(x - value) < tolerance


def get_volume(geometry: W.triangulation) -> float:
    """Calculates the total internal volume of a geometry

    Volumes of non-manifold geometry will be unpredictable.

    :param geometry: Geometry output calculated by IfcOpenShell
    :return: The volume in m3
    """

    # https://stackoverflow.com/questions/1406029/how-to-calculate-the-volume-of-a-3d-mesh-object-the-surface-of-which-is-made-up
    def signed_triangle_volume(p1, p2, p3):
        v321 = p3[0] * p2[1] * p1[2]
        v231 = p2[0] * p3[1] * p1[2]
        v312 = p3[0] * p1[1] * p2[2]
        v132 = p1[0] * p3[1] * p2[2]
        v213 = p2[0] * p1[1] * p3[2]
        v123 = p1[0] * p2[1] * p3[2]
        return (1.0 / 6.0) * (-v321 + v231 + v312 - v132 - v213 + v123)

    # Can't optimize it using buffers - performance seems to get only worse.
    verts = geometry.verts
    faces = geometry.faces
    grouped_verts = [[verts[i], verts[i + 1], verts[i + 2]] for i in range(0, len(verts), 3)]
    volumes = [
        signed_triangle_volume(grouped_verts[faces[i]], grouped_verts[faces[i + 1]], grouped_verts[faces[i + 2]])
        for i in range(0, len(faces), 3)
    ]
    return abs(sum(volumes))


def get_x(geometry: W.triangulation) -> float:
    """Calculates the X length of the geometry

    :param geometry: Geometry output calculated by IfcOpenShell
    :return: The X dimension
    """
    verts_flat = get_vertices(geometry).ravel()
    return (np.max(verts_flat[0::3]) - np.min(verts_flat[0::3])).item()


def get_y(geometry: W.triangulation) -> float:
    """Calculates the Y length of the geometry

    :param geometry: Geometry output calculated by IfcOpenShell
    :return: The Y dimension
    """
    verts_flat = get_vertices(geometry).ravel()
    return (np.max(verts_flat[1::3]) - np.min(verts_flat[1::3])).item()


def get_z(geometry: W.triangulation) -> float:
    """Calculates the Z length of the geometry

    :param geometry: Geometry output calculated by IfcOpenShell
    :return: The Z dimension
    """
    verts_flat = get_vertices(geometry).ravel()
    return (np.max(verts_flat[2::3]) - np.min(verts_flat[2::3])).item()


def get_max_xy(geometry: W.triangulation) -> float:
    """Gets the maximum X or Y length of the geometry

    :param geometry: Geometry output calculated by IfcOpenShell
    :return: The maximum possible value out of the X and Y dimension
    """
    return max(get_x(geometry), get_y(geometry))


def get_max_xyz(geometry: W.triangulation) -> float:
    """Gets the maximum X, Y, or Z length of the geometry

    :param geometry: Geometry output calculated by IfcOpenShell
    :return: The maximum possible value out of the X, Y, and Z dimension
    """
    return max(get_x(geometry), get_y(geometry), get_z(geometry))


def get_min_xyz(geometry: W.triangulation) -> float:
    """Gets the minimum X, Y, or Z length of the geometry

    :param geometry: Geometry output calculated by IfcOpenShell
    :return: The minimum possible value out of the X, Y, and Z dimension
    """
    return min(get_x(geometry), get_y(geometry), get_z(geometry))


def get_shape_matrix(shape: ShapeElementType) -> MatrixType:
    """Formats the transformation matrix of a shape as a 4x4 numpy array

    :param shape: Shape output calculated by IfcOpenShell
    :return: A 4x4 numpy array representing the transformation matrix
    """
    return np.frombuffer(shape.transformation_buffer, "d").reshape((4, 4), order="F")


def get_bbox_centroid(geometry: W.triangulation) -> tuple[float, float, float]:
    """Calculates the bounding box centroid of the geometry

    The centroid is in local coordinates relative to the object's placement.

    :param geometry: Geometry output calculated by IfcOpenShell
    :return: A tuple representing the XYZ centroid
    """
    vertices_array = get_vertices(geometry)
    return (np.min(vertices_array, axis=0) + np.max(vertices_array, axis=0)) / 2


def get_vert_centroid(geometry: W.triangulation) -> tuple[float, float, float]:
    """Calculates the average vertex centroid of the geometry

    The centroid is in local coordinates relative to the object's placement.

    :param geometry: Geometry output calculated by IfcOpenShell
    :return: A tuple representing the XYZ centroid
    """
    return np.mean(get_vertices(geometry), axis=0)


def get_element_bbox_centroid(
    element: ifcopenshell.entity_instance, geometry: W.triangulation
) -> npt.NDArray[np.float64]:
    """Calculates the element's bounding box centroid

    The centroid is in global coordinates. Note that if you have the shape, it
    is more efficient to use :func:`get_shape_bbox_centroid`.

    :param element: The element occurrence
    :param geometry: Geometry output calculated by IfcOpenShell
    :return: A tuple representing the XYZ centroid
    """
    centroid = get_bbox_centroid(geometry)
    if not element.ObjectPlacement or not element.ObjectPlacement.is_a("IfcLocalPlacement"):
        return np.array(centroid)
    mat = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
    return (mat @ np.array([*centroid, 1.0]))[0:3]


def get_shape_bbox_centroid(shape: ShapeElementType, geometry: W.triangulation) -> npt.NDArray[np.float64]:
    """Calculates the shape's bounding box centroid

    The centroid is in global coordinates. Note that if you do not have the
    shape, you can use :func:`get_element_bbox_centroid`.

    :param shape: Shape output calculated by IfcOpenShell
    :param geometry: Geometry output calculated by IfcOpenShell
    :return: A tuple representing the XYZ centroid
    """
    centroid = get_bbox_centroid(geometry)
    return (get_shape_matrix(shape) @ np.array([*centroid, 1.0]))[0:3]


def get_vertices(geometry: W.triangulation, is_2d: bool = False) -> npt.NDArray[np.float64]:
    """Get all the vertices as a numpy array

    Vertices are in local coordinates.

    :param geometry: Geometry output calculated by IfcOpenShell
    :param is_2d: Set to True to to get XY coordinates only.
    :return: A numpy array listing all the vertices and their coordinates.
        Array shape: (n, 3), where n - number of vertices.
    """
    if is_2d:
        return np.frombuffer(geometry.verts_buffer, "d").reshape(-1, 3)[:, :2]
    return np.frombuffer(geometry.verts_buffer, "d").reshape(-1, 3)


def get_edges(geometry: W.triangulation) -> npt.NDArray[np.int32]:
    """Get all the edges as a numpy array

    Results are a nested numpy array e.g. [[e1v1, e1v2], [e2v1, e2v2], ...]

    Note that although geometry always holds triangulated faces, edges will
    represent the original tessellation or BRep's faces, which may be quads or
    ngons.

    :param geometry: Geometry output calculated by IfcOpenShell
    :return: A numpy array listing all the edges.
        Array shape: (n, 2), where n - number of edges.
    """
    return np.frombuffer(geometry.edges_buffer, dtype="i").reshape(-1, 2)


def get_faces(geometry: W.triangulation) -> npt.NDArray[np.int32]:
    """Get all the faces as a numpy array

    Faces are always triangulated. If the shape is a BRep and you want to get
    the original untriangulated output, refer to :func:`get_edges`.

    Results are a nested numpy array e.g. [[f1v1, f1v2, f1v3], [f2v1, f2v2, f2v3], ...]

    :param geometry: Geometry output calculated by IfcOpenShell
    :return: A numpy array listing all the faces.
        Array shape: (n, 3), where n - number of faces.
    """
    return np.frombuffer(geometry.faces_buffer, dtype="i").reshape(-1, 3)


def get_material_colors(geometry: W.triangulation) -> npt.NDArray[np.float64]:
    """Get material colors as a numpy array.

    :return: A numpy array listing RGBA color for each shape's material.
        Array shape: (1, 4).
    """
    # colors_buffer comes from geometry.materials and doesn't account
    # for colors that can be set by some other way (e.g. IfcIndexedColourMap).
    return np.frombuffer(geometry.colors_buffer, dtype="d").reshape(-1, 4)


def get_normals(geometry: W.triangulation) -> npt.NDArray[np.float64]:
    """Get vertex normals as a numpy array.

    See geometry settings documentation for settings that affect normals.

    :return: A numpy array listing normal for each shape vertex.
        Array shape: (1, 3).
    """
    return np.frombuffer(geometry.normals_buffer, dtype="d").reshape(-1, 3)


def get_shape_material_styles(geometry: W.triangulation) -> tuple[W.style, ...]:
    """Get list of material styles."""
    return geometry.materials


def get_faces_material_style_ids(geometry: W.triangulation) -> npt.NDArray[np.int32]:
    """Get material styles ids for the geometry faces.

    Return a list of corresponding indices of styles from get_shape_material_styles for each face.
    If face has no style assigned, index -1 is used.
    """
    return np.frombuffer(geometry.material_ids_buffer, dtype="i")


def get_faces_representation_item_ids(geometry: W.triangulation) -> npt.NDArray[np.int32]:
    """Get representation item ids for the geometry faces."""
    return np.frombuffer(geometry.item_ids_buffer, dtype="i")


def get_edges_representation_item_ids(geometry: W.triangulation) -> npt.NDArray[np.int32]:
    """Get representation item ids for the geometry edges.

    Can be useful for geometry without faces and in general is more universal
    since it's possible that geometry will have elements with and without faces.
    """
    return np.frombuffer(geometry.edges_item_ids_buffer, dtype="i")


def get_shape_vertices(shape: ShapeElementType, geometry: W.triangulation) -> npt.NDArray[np.float64]:
    """Get the shape's vertices as a numpy array

    Vertices are in global coordinates. If you do not have the shape, you can
    use :func:`get_element_vertices`.

    Results are a nested numpy array e.g. [[v1x, v1y, v1z], [v2x, v2y, v2z], ...]

    :param shape: Shape output calculated by IfcOpenShell
    :param geometry: Geometry output calculated by IfcOpenShell
    :return: A numpy array listing all the vertices. Each vertex is a numpy array with XYZ coordinates.
        Array shape: (n, 3), where n - number of vertices.
    """
    verts = get_vertices(geometry)
    mat = get_shape_matrix(shape)
    return np.delete((mat @ np.hstack((verts, np.ones((len(verts), 1)))).T).T, -1, axis=1)


def get_element_vertices(element: ifcopenshell.entity_instance, geometry: W.triangulation) -> npt.NDArray[np.float64]:
    """Get the element's vertices as a numpy array

    Vertices are in global coordinates. Note that if you have the shape, it is
    more efficient to use :func:`get_shape_vertices`.

    Results are a nested numpy array e.g. [[v1x, v1y, v1z], [v2x, v2y, v2z], ...]

    :param element: The element occurrence
    :param geometry: Geometry output calculated by IfcOpenShell
    :return: A numpy array listing all the vertices. Each vertex is a numpy array with XYZ coordinates.
    """
    verts = get_vertices(geometry)
    if not element.ObjectPlacement or not element.ObjectPlacement.is_a("IfcLocalPlacement"):
        return verts
    mat = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
    return np.delete((mat @ np.hstack((verts, np.ones((len(verts), 1)))).T).T, -1, axis=1)


def get_bottom_elevation(geometry: W.triangulation) -> float:
    """Gets the lowest local Z ordinate of the geometry

    :param geometry: Geometry output calculated by IfcOpenShell
    :return: The Z value
    """
    verts_flat = get_vertices(geometry).ravel()
    return np.min(verts_flat[2::3]).item()


def get_top_elevation(geometry: W.triangulation) -> float:
    """Gets the highest local Z ordinate of the geometry

    :param geometry: Geometry output calculated by IfcOpenShell
    :return: The Z value
    """
    verts_flat = get_vertices(geometry).ravel()
    return np.max(verts_flat[2::3]).item()


def get_shape_bottom_elevation(shape: ShapeElementType, geometry: W.triangulation) -> float:
    """Gets the lowest global Z ordinate of the shape

    If you do not have the shape, you can use :func:`get_element_bottom_elevation`
    instead.

    :param shape: Shape output calculated by IfcOpenShell
    :param geometry: Geometry output calculated by IfcOpenShell
    :return: The Z value
    """
    return min([v[2] for v in get_shape_vertices(shape, geometry)])


def get_shape_top_elevation(shape: ShapeElementType, geometry: W.triangulation) -> float:
    """Gets the highest global Z ordinate of the shape

    If you do not have the shape, you can use :func:`get_element_top_elevation`
    instead.

    :param shape: Shape output calculated by IfcOpenShell
    :param geometry: Geometry output calculated by IfcOpenShell
    :return: The Z value
    """
    return max([v[2] for v in get_shape_vertices(shape, geometry)])


def get_element_bottom_elevation(element: ifcopenshell.entity_instance, geometry: W.triangulation) -> float:
    """Gets the lowest global Z ordinate of the element

    Note that if you have the shape, it is more efficient to use
    :func:`get_shape_bottom_elevation`.

    :param element: The element occurrence
    :param geometry: Geometry output calculated by IfcOpenShell
    :return: The Z value
    """
    return min([v[2] for v in get_element_vertices(element, geometry)])


def get_element_top_elevation(element: ifcopenshell.entity_instance, geometry: W.triangulation) -> float:
    """Gets the highest global Z ordinate of the element

    Note that if you have the shape, it is more efficient to use
    :func:`get_shape_top_elevation`.

    :param element: The element occurrence
    :param geometry: Geometry output calculated by IfcOpenShell
    :return: The Z value
    """
    return max([v[2] for v in get_element_vertices(element, geometry)])


def get_bbox(vertices: npt.NDArray[np.float64]) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    """Gets the bounding box of vertices

    :param vertices: An iterable of vertices
    :return: The bounding box value represented as a tuple of two numpy arrays.
        The first holds the bottom left corner and the second holds the top
        right.  E.g.  (np.array([minx, miny, minz]), np.array([maxx, maxy,
        maxz]))
    """
    return (np.min(vertices, axis=0), np.max(vertices, axis=0))


def get_area_vf(vertices: npt.NDArray[np.float64], faces: npt.NDArray[np.int32]) -> float:
    """Calculates the surface area given a list of vertices and triangulated faces

    :param vertices: A list of 3D vertices, such as returned from get_vertices.
    :param faces: A list of faces, such as returned from get_faces.
    :return: The surface area.
    """
    # Calculate the triangle normal vectors
    v1 = vertices[faces[:, 1]] - vertices[faces[:, 0]]
    v2 = vertices[faces[:, 2]] - vertices[faces[:, 0]]
    triangle_normals = np.cross(v1, v2)

    # Normalize the normal vectors to get their length (i.e., triangle area)
    triangle_areas = np.linalg.norm(triangle_normals, axis=1) / 2

    # Sum up the areas to get the total area of the mesh
    mesh_area = np.sum(triangle_areas)

    return mesh_area.item()


def get_area(geometry: W.triangulation) -> float:
    """Calculates the surface area of the geometry

    :param geometry: Geometry output calculated by IfcOpenShell
    :return: The surface area.
    """
    vertices = get_vertices(geometry)
    faces = get_faces(geometry)
    return get_area_vf(vertices, faces)


def get_side_area(
    geometry: W.triangulation,
    axis: AXIS_LITERAL = "Y",
    direction: Optional[VectorType] = None,
    angle: float = 90.0,
) -> float:
    """Calculates the total surface area of surfaces that are visible from the specified axis

    This is typically useful for calculating elevational areas. For example,
    you might want to calculate the side area of a wall (i.e. only one side,
    not both).

    Surfaces do not need to be exactly perpendicular in the direction of the
    specified axis. A surface is counted so long as it is visible from that
    axis.

    Note that this calculates the actual area, not the projected 2D area. If
    you want the projected area, use :func:`get_footprint_area`.

    :param geometry: Geometry output calculated by IfcOpenShell
    :param axis: Either X, Y, or Z. Defaults to Y, which is used for standard
        walls.
    :param angle: Accept angle difference between face and axis, in degrees.
        E.g. default angle 90 will find all faces with angle < 90 degrees.
    :return: The surface area.
    """
    if direction is None:
        direction = {"X": (1.0, 0.0, 0.0), "Y": (0.0, 1.0, 0.0), "Z": (0.0, 0.0, 1.0)}[axis]

    vertices = get_vertices(geometry)
    faces = get_faces(geometry)

    # Calculate the triangle normal vectors
    v1 = vertices[faces[:, 1]] - vertices[faces[:, 0]]
    v2 = vertices[faces[:, 2]] - vertices[faces[:, 0]]
    triangle_normals = np.cross(v1, v2)

    # Normalize the normal vectors
    triangle_normals = triangle_normals / np.linalg.norm(triangle_normals, axis=1)[:, np.newaxis]
    direction = np.array(direction) / np.linalg.norm(direction)

    # Find the faces with a normal vector pointing in the desired +Y normal direction
    # normal_tol < 0 is pointing away, = 0 is perpendicular, and > 0 is pointing towards.
    normal_tol = 0.01  # For angle 90 it's close to perpendicular, but with a fuzz for numerical tolerance
    acceptable_dot = cos(radians(angle)) + normal_tol
    dot_products = np.dot(triangle_normals, direction)
    filtered_face_indices = np.where(dot_products > acceptable_dot)[0]
    filtered_faces = faces[filtered_face_indices]
    return get_area_vf(vertices, filtered_faces)


def get_max_side_area(geometry: W.triangulation) -> float:
    """Returns the maximum X, Y, or Z side area

    See :func:`get_side_area` for how side area is calculated.

    :param geometry: Geometry output calculated by IfcOpenShell
    :return: The maximum surface area from either the X, Y, or Z axis.
    """
    return max(get_side_area(geometry, axis="X"), get_side_area(geometry, axis="Y"), get_side_area(geometry, axis="Z"))


def get_top_area(geometry: W.triangulation) -> float:
    return get_side_area(geometry, axis="Z", angle=45)


def get_footprint_area(
    geometry: W.triangulation,
    axis: AXIS_LITERAL = "Z",
    direction: Optional[VECTOR_3D] = None,
) -> float:
    """Calculates the total footprint (i.e. projected) surface area visible from along an axis

    This is typically useful for calculating footprint areas. For example, you
    might want to calculate the top-down footprint area of a slab, ignoring
    slopes in the slab.

    Surfaces do not need to be exactly perpendicular in the direction of the
    specified axis. A surface is counted so long as it is visible from that
    axis.

    Note that this calculates the 2D projected area, not the actual surface
    area. If you want the actual area, use :func:`get_side_area`.

    :param geometry: Geometry output calculated by IfcOpenShell
    :param axis: Either X, Y, or Z. Defaults to Z.
    :param direction: An XYZ iterable (e.g. (0., 0., 1.)). If a direction
        vector is specified, this overrides the axis argument.
    :return: The surface area.
    """
    if direction is None:
        direction = {"X": (1.0, 0.0, 0.0), "Y": (0.0, 1.0, 0.0), "Z": (0.0, 0.0, 1.0)}[axis]

    vertices = get_vertices(geometry)
    faces = get_faces(geometry)

    # Calculate the triangle normal vectors
    v1 = vertices[faces[:, 1]] - vertices[faces[:, 0]]
    v2 = vertices[faces[:, 2]] - vertices[faces[:, 0]]
    triangle_normals = np.cross(v1, v2)

    # Normalize the normal vectors
    triangle_normals = triangle_normals / np.linalg.norm(triangle_normals, axis=1)[:, np.newaxis]
    direction = np.array(direction) / np.linalg.norm(direction)

    # Find the faces with a normal vector pointing in the desired direction using dot product
    # normal_tol < 0 is pointing away, = 0 is perpendicular, and > 0 is pointing towards.
    normal_tol = 0.01  # Close to perpendicular, but with a fuzz for numerical tolerance
    dot_products = np.dot(triangle_normals, direction)
    filtered_face_indices = np.where(dot_products > normal_tol)[0]
    filtered_faces = faces[filtered_face_indices]

    # Flatten vertices along the direction
    vertices = vertices.copy()  # Buffers are read-only.
    for idx in range(len(vertices)):
        vertices[idx] = vertices[idx] - np.dot(vertices[idx], direction) * direction

    # Now flatten 3D vertices into 2D polygons which can be unioned to find a footprint.

    # Create an orthonormal basis using the direction
    d = np.array(direction) / np.linalg.norm(direction)

    # Find a vector not parallel to d
    a = np.array(d)
    if not np.isclose(a[2], 1.0, atol=0.01):  # If d is not along the Z-axis
        a[2] += 0.01  # Small perturbation to make it not parallel
    else:
        a = np.array([1, 0, 0])

    # First basis vector
    b = np.cross(d, a)
    b /= np.linalg.norm(b)

    # Second basis vector
    c = np.cross(d, b)

    # Project the flattened vertices onto the basis to get 2D coordinates
    vertices_2d = np.array([[np.dot(v, b), np.dot(v, c)] for v in vertices])

    polygons = [shapely.Polygon(vertices_2d[face]) for face in filtered_faces]
    unioned_polygon = shapely.ops.unary_union(polygons)

    return unioned_polygon.area


def get_outer_surface_area(geometry: W.triangulation) -> float:
    """Calculates the outer surface area (i.e. all sides except for top and bottom)

    This is typically useful for calculating painted areas of beams which
    exclude the end faces (at the minimum and maximum local Z).

    :param geometry: Geometry output calculated by IfcOpenShell
    :return: The surface area.
    """
    vertices = get_vertices(geometry)
    faces = get_faces(geometry)

    # Calculate the triangle normal vectors
    v1 = vertices[faces[:, 1]] - vertices[faces[:, 0]]
    v2 = vertices[faces[:, 2]] - vertices[faces[:, 0]]
    triangle_normals = np.cross(v1, v2)

    # Normalize the normal vectors
    triangle_normals = triangle_normals / np.linalg.norm(triangle_normals, axis=1)[:, np.newaxis]

    # Find the faces with a normal vector that isn't +Z or -Z
    filtered_face_indices = np.where(abs(triangle_normals[:, 2]) < tol)[0]
    filtered_faces = faces[filtered_face_indices]
    return get_area_vf(vertices, filtered_faces)


def get_footprint_perimeter(geometry: W.triangulation) -> float:
    """Calculates the footprint perimeter of the geometry

    All faces with a negative Z normal are considered and the distance of all
    perimeter edges are totaled.

    :param geometry: Geometry output calculated by IfcOpenShell
    :return: The perimeter length
    """
    vertices = get_vertices(geometry)
    faces = get_faces(geometry)

    # Calculate the triangle normal vectors
    v1 = vertices[faces[:, 1]] - vertices[faces[:, 0]]
    v2 = vertices[faces[:, 2]] - vertices[faces[:, 0]]
    triangle_normals = np.cross(v1, v2)

    # Normalize the normal vectors
    triangle_normals = triangle_normals / np.linalg.norm(triangle_normals, axis=1)[:, np.newaxis]

    # Find the faces with a normal vector pointing in the negative Z direction
    negative_z_face_indices = np.where(triangle_normals[:, 2] < -tol)[0]
    negative_z_faces = faces[negative_z_face_indices]

    # Initialize the set of counted edges and the perimeter
    all_edges = set()
    shared_edges = set()
    perimeter = 0

    # Loop through each face
    for face in negative_z_faces:
        # Loop through each edge of the face
        for i in range(3):
            # Get the indices of the two vertices that define the edge
            edge = (face[i], face[(i + 1) % 3])
            # Keep track of shared edges. Perimeter edges are unshared.
            if (edge[1], edge[0]) in all_edges or (edge[0], edge[1]) in all_edges:
                shared_edges.add((edge[0], edge[1]))
                shared_edges.add((edge[1], edge[0]))
            else:
                all_edges.add(edge)

    return np.sum([np.linalg.norm(vertices[e[0]] - vertices[e[1]]) for e in (all_edges - shared_edges)]).item()


def get_profiles(element: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    """Gets all 2D profiles used in the definition of a parametric shape

    Profiles may be retrieved either from material profile sets or from swept
    solid extrusions. This is useful for later doing 2D take-off from profiles.

    :param element: The element occurrence
    :return: A list of profiles
    """
    material = ifcopenshell.util.element.get_material(element, should_skip_usage=True)
    if material and material.is_a("IfcMaterialProfileSet"):
        return [mp.Profile for mp in material.MaterialProfiles]
    return [e.SweptArea for e in get_extrusions(element)]


def get_extrusions(element: ifcopenshell.entity_instance) -> Union[list[ifcopenshell.entity_instance], None]:
    """Gets all extruded area solids used to define an element's model body geometry

    :param element: The element occurrence
    :return: A list of extrusion representation items or `None` if element has no representation.
    """
    representation = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
    if not representation:
        return
    representation = ifcopenshell.util.representation.resolve_representation(representation)
    extrusions = []
    for item in representation.Items:
        while True:
            if item.is_a("IfcExtrudedAreaSolid"):
                extrusions.append(item)
                break
            elif item.is_a("IfcBooleanResult"):
                item = item.FirstOperand
            else:
                break
    return extrusions


def get_base_extrusions(element: ifcopenshell.entity_instance) -> Union[list[ifcopenshell.entity_instance], None]:
    """Gets all base extrusions used to define an element's model body geometry

    A base extrusion is assumed to be an extrusion prior to all boolean
    results.

    :param element: The element occurrence
    :return: A list of extrusion representation items or `None` if element has no representation.
    """
    if not (rep := ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")):
        return
    extrusions = []
    for item in ifcopenshell.util.representation.resolve_representation(rep).Items:
        while item.is_a("IfcBooleanResult"):
            item = item.FirstOperand
        if item.is_a("IfcExtrudedAreaSolid"):
            extrusions.append(item)
    return extrusions


def get_total_edge_length(geometry: W.triangulation) -> float:
    """Calculates the total length of edges in a given geometry.

    :param geometry: Geometry output calculated by IfcOpenShell
    :return: The total length of all edges in the geometry.
    """
    vertices = get_vertices(geometry)
    vertices = vertices[get_edges(geometry)]
    return np.linalg.norm(vertices[:, 1] - vertices[:, 0], axis=1).sum().item()


def _extend_line(start: np.ndarray, end: np.ndarray, distance: float) -> tuple[np.ndarray, np.ndarray]:
    """Extend a line segment by a fixed distance on both ends.

    :param start: (x, y) or (x, y, z) array.
    :param end: (x, y) or (x, y, z) array.
    :param distance: Distance to extend on each end.
    :return: (new_start, new_end) arrays.
    """
    direction = end - start
    norm = np.linalg.norm(direction)
    if norm == 0:
        return start, end
    offset = distance * (direction / norm)
    return start - offset, end + offset


def bisect_mesh_plane_vf(
    verts: npt.NDArray[np.float64],
    faces: npt.NDArray[np.int32],
    plane_z: float,
    *,
    precision: int = 3,
    extend: float = 0.0,
) -> list:
    """Intersect a triangulated mesh with a horizontal Z plane.

    All faces are processed at once via numpy broadcasting for performance.

    :param verts: (n, 3) array of vertices in world coordinates.
    :param faces: (m, 3) array of triangle vertex indices.
    :param plane_z: Z elevation of the horizontal cutting plane.
    :param precision: Decimal places to round intersection point coordinates to.
    :param extend: Distance to extend each segment on both ends, to ensure
        overlap with neighbouring segments for polygon closure.
    :return: List of (start_xy, end_xy) tuples where each coordinate is (x, y).
    """
    if len(faces) == 0:
        return []
    v0 = verts[faces[:, 0]]
    v1 = verts[faces[:, 1]]
    v2 = verts[faces[:, 2]]
    d0 = v0[:, 2] - plane_z
    d1 = v1[:, 2] - plane_z
    d2 = v2[:, 2] - plane_z
    straddle = ~((np.minimum(np.minimum(d0, d1), d2) > 0) | (np.maximum(np.maximum(d0, d1), d2) < 0))
    if not np.any(straddle):
        return []
    idx = np.where(straddle)[0]
    d0s, d1s, d2s = d0[idx], d1[idx], d2[idx]
    v0s, v1s, v2s = v0[idx], v1[idx], v2[idx]

    def _edge_intersections(va, vb, da, db):
        mask = da * db < 0
        diff = da - db
        diff = np.where(diff == 0, 1.0, diff)
        t = np.where(mask, da / diff, 0.0)
        pts = va + t[:, np.newaxis] * (vb - va)
        return pts, mask

    p01, m01 = _edge_intersections(v0s, v1s, d0s, d1s)
    p12, m12 = _edge_intersections(v1s, v2s, d1s, d2s)
    p20, m20 = _edge_intersections(v2s, v0s, d2s, d0s)

    segments = []
    for i in range(len(idx)):
        pts_xy = []
        for pt, mask in ((p01[i], m01[i]), (p12[i], m12[i]), (p20[i], m20[i])):
            if mask:
                pts_xy.append((round(float(pt[0]), precision), round(float(pt[1]), precision)))
        if len(pts_xy) == 2 and pts_xy[0] != pts_xy[1]:
            if extend > 0:
                s, e = _extend_line(np.array(pts_xy[0]), np.array(pts_xy[1]), extend)
                segments.append((s.tolist(), e.tolist()))
            else:
                segments.append(pts_xy)
    return segments


def dissolve_faces(
    verts: npt.NDArray[np.float64],
    faces: npt.NDArray[np.int32],
    edges: npt.NDArray[np.int32],
    merge_coplanar: bool = False,
    angle_tolerance: float = 0.017453292519943295,
) -> list[list[int]]:
    """Reconstruct polygonal faces from triangulated mesh data.

    Uses the original (pre-triangulation) edges from ``get_edges`` to
    identify which triangle edges are internal (to be merged) vs external
    (ngon boundaries). Triangles connected by internal edges are grouped
    into polygonal faces.

    When ``merge_coplanar`` is True, a second pass merges adjacent ngons
    whose face normals are parallel within ``angle_tolerance`` radians.
    This mirrors ``bmesh.ops.dissolve_limit`` behavior where coplanar
    faces sharing an edge are merged regardless of the original face
    structure. This is needed when the IFC representation splits a single
    planar face into multiple faces (e.g. an L-shaped top face split into
    triangles + quads).

    :param verts: (n, 3) array of vertices.
    :param faces: (m, 3) array of triangle vertex indices.
    :param edges: (e, 2) array of original (pre-triangulation) edge vertex
        indices, as returned by :func:`get_edges`.
    :param merge_coplanar: If True, merge adjacent coplanar ngons.
    :param angle_tolerance: Angle in radians for coplanar merge (default 1°).
    :return: List of polygonal faces, each as an ordered list of vertex indices
        forming a closed polygon (last vertex connects back to first).
    """
    if len(faces) == 0:
        return []
    if len(edges) == 0:
        return [list(f) for f in faces]

    original_edges = {frozenset((int(e[0]), int(e[1]))) for e in edges}

    tri_edges = []
    for f in faces:
        tri_edges.append(
            (
                frozenset((int(f[0]), int(f[1]))),
                frozenset((int(f[1]), int(f[2]))),
                frozenset((int(f[2]), int(f[0]))),
            )
        )

    internal_edge_to_tris: dict[frozenset, list[int]] = {}
    for tri_idx, edges_3 in enumerate(tri_edges):
        for e in edges_3:
            if e not in original_edges:
                internal_edge_to_tris.setdefault(e, []).append(tri_idx)

    parent = list(range(len(faces)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    for tri_indices in internal_edge_to_tris.values():
        if len(tri_indices) == 2:
            union(tri_indices[0], tri_indices[1])

    ngons: dict[int, list[int]] = {}
    for tri_idx in range(len(faces)):
        root = find(tri_idx)
        ngons.setdefault(root, []).append(tri_idx)

    if merge_coplanar:
        _merge_coplanar_ngons(ngons, faces, verts, tri_edges, parent, find, union, angle_tolerance)

    result = []
    for tri_indices in ngons.values():
        tri_edge_set = set()
        edge_count: dict[frozenset, int] = {}
        for tri_idx in tri_indices:
            for e in tri_edges[tri_idx]:
                tri_edge_set.add(e)
                edge_count[e] = edge_count.get(e, 0) + 1

        if merge_coplanar:
            boundary_edges = [e for e in tri_edge_set if edge_count.get(e, 0) == 1]
        else:
            boundary_edges = [e for e in tri_edge_set if e in original_edges]

        if not boundary_edges:
            result.append(list(faces[tri_indices[0]]))
            continue

        edge_adjacency: dict[int, int] = {}
        for e in boundary_edges:
            v_list = list(e)
            for tri_idx in tri_indices:
                f = faces[tri_idx]
                f_edges = [(int(f[0]), int(f[1])), (int(f[1]), int(f[2])), (int(f[2]), int(f[0]))]
                for fe in f_edges:
                    if frozenset(fe) == e:
                        edge_adjacency[fe[0]] = fe[1]
                        break
                else:
                    continue
                break

        if not edge_adjacency:
            result.append(list(faces[tri_indices[0]]))
            continue

        start = next(iter(edge_adjacency))
        polygon = [start]
        current = edge_adjacency[start]
        while current != start and current in edge_adjacency:
            polygon.append(current)
            current = edge_adjacency[current]

        if len(polygon) >= 3:
            result.append(polygon)
        else:
            result.append(list(faces[tri_indices[0]]))

    return result


def _merge_coplanar_ngons(
    ngons: dict[int, list[int]],
    faces: npt.NDArray[np.int32],
    verts: npt.NDArray[np.float64],
    tri_edges: list,
    parent: list[int],
    find,
    union,
    angle_tolerance: float,
) -> None:
    """Merge adjacent ngons whose face normals are parallel within tolerance.

    Modifies ``ngons`` and ``parent`` in place.
    """
    from math import acos

    # Compute normal for each ngon
    ngon_normals: dict[int, np.ndarray] = {}
    ngon_edge_to_ngons: dict[frozenset, list[int]] = {}
    ngon_roots = list(ngons.keys())

    for root in ngon_roots:
        tri_indices = ngons[root]
        f0 = faces[tri_indices[0]]
        v0, v1, v2 = verts[f0[0]], verts[f0[1]], verts[f0[2]]
        edge1 = v1 - v0
        edge2 = v2 - v0
        normal = np.cross(edge1, edge2)
        norm = np.linalg.norm(normal)
        if norm > 1e-8:
            normal = normal / norm
        ngon_normals[root] = normal

        # Collect all edges of this ngon
        ngon_edges = set()
        for tri_idx in tri_indices:
            for e in tri_edges[tri_idx]:
                ngon_edges.add(e)
        for e in ngon_edges:
            ngon_edge_to_ngons.setdefault(e, []).append(root)

    # Find shared edges between different ngons and check coplanarity
    for edge, root_list in ngon_edge_to_ngons.items():
        if len(root_list) != 2:
            continue
        root_a, root_b = root_list[0], root_list[1]
        if root_a == root_b:
            continue
        # Check if already merged
        ra, rb = find(root_a), find(root_b)
        if ra == rb:
            continue
        # Compare normals
        na, nb = ngon_normals[root_a], ngon_normals[root_b]
        dot = max(min(float(np.dot(na, nb)), 1.0), -1.0)
        angle = acos(dot)
        if angle < angle_tolerance:
            union(root_a, root_b)

    # Rebuild ngons dict with merged groups
    new_ngons: dict[int, list[int]] = {}
    for root in ngon_roots:
        new_root = find(root)
        new_ngons.setdefault(new_root, []).extend(ngons[root])
    ngons.clear()
    ngons.update(new_ngons)
