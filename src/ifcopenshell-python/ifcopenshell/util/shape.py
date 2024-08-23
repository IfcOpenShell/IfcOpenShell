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

import shapely
import shapely.ops
import numpy as np
import numpy.typing as npt
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation
from ifcopenshell.geom import ShapeElementType, ShapeType
from typing import Optional, Literal, Union, Iterable

tol = 1e-6
AXIS_LITERAL = Literal["X", "Y", "Z"]
VECTOR_3D = tuple[float, float, float]

MatrixType = npt.NDArray[np.float64]
"""`npt.NDArray[np.float64]`"""

# NOTE: See IfcGeomRepresentation.h for ShapeType buffer types.


def is_x(value: float, x: float, tolerance: Optional[float] = None) -> bool:
    """Checks whether a value is equivalent to X given a tolerance

    :param value: Input value
    :type value: float
    :param x: The value to compare to
    :type x: float
    :param tolerance: The tolerance to use. Defaults to 1e-6.
    :type tolerance: float
    :return: True or false
    :rtype: bool
    """
    if tolerance is None:
        tolerance = tol
    return abs(x - value) < tolerance


def get_volume(geometry: ShapeType) -> float:
    """Calculates the total internal volume of a geometry

    Volumes of non-manifold geometry will be unpredictable.

    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :return: The volume in m3
    :rtype: float
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


def get_x(geometry: ShapeType) -> float:
    """Calculates the X length of the geometry

    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :return: The X dimension
    :rtype: float
    """
    verts_flat = get_vertices(geometry).ravel()
    return np.max(verts_flat[0::3]) - np.min(verts_flat[0::3])


def get_y(geometry: ShapeType) -> float:
    """Calculates the Y length of the geometry

    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :return: The Y dimension
    :rtype: float
    """
    verts_flat = get_vertices(geometry).ravel()
    return np.max(verts_flat[1::3]) - np.min(verts_flat[1::3])


def get_z(geometry: ShapeType) -> float:
    """Calculates the Z length of the geometry

    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :return: The Z dimension
    :rtype: float
    """
    verts_flat = get_vertices(geometry).ravel()
    return np.max(verts_flat[2::3]) - np.min(verts_flat[2::3])


def get_max_xy(geometry: ShapeType) -> float:
    """Gets the maximum X or Y length of the geometry

    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :return: The maximum possible value out of the X and Y dimension
    :rtype: float
    """
    return max(get_x(geometry), get_y(geometry))


def get_max_xyz(geometry: ShapeType) -> float:
    """Gets the maximum X, Y, or Z length of the geometry

    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :return: The maximum possible value out of the X, Y, and Z dimension
    :rtype: float
    """
    return max(get_x(geometry), get_y(geometry), get_z(geometry))


def get_min_xyz(geometry: ShapeType) -> float:
    """Gets the minimum X, Y, or Z length of the geometry

    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :return: The minimum possible value out of the X, Y, and Z dimension
    :rtype: float
    """
    return min(get_x(geometry), get_y(geometry), get_z(geometry))


def get_shape_matrix(shape: ShapeElementType) -> MatrixType:
    """Formats the transformation matrix of a shape as a 4x4 numpy array

    :param shape: Shape output calculated by IfcOpenShell
    :type shape: shape
    :return: A 4x4 numpy array representing the transformation matrix
    :rtype: MatrixType
    """
    return np.array(shape.transformation.matrix).reshape((4, 4), order="F")


def get_bbox_centroid(geometry: ShapeType) -> tuple[float, float, float]:
    """Calculates the bounding box centroid of the geometry

    The centroid is in local coordinates relative to the object's placement.

    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :return: A tuple representing the XYZ centroid
    :rtype: tuple[float, float, float]
    """
    vertices_array = get_vertices(geometry)
    return (np.min(vertices_array, axis=0) + np.max(vertices_array, axis=0)) / 2


def get_vert_centroid(geometry: ShapeType) -> tuple[float, float, float]:
    """Calculates the average vertex centroid of the geometry

    The centroid is in local coordinates relative to the object's placement.

    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :return: A tuple representing the XYZ centroid
    :rtype: tuple[float, float, float]
    """
    return np.mean(get_vertices(geometry), axis=0)


def get_element_bbox_centroid(element: ifcopenshell.entity_instance, geometry) -> npt.NDArray[np.float64]:
    """Calculates the element's bounding box centroid

    The centroid is in global coordinates. Note that if you have the shape, it
    is more efficient to use ``get_shape_bbox_centroid``.

    :param element: The element occurrence
    :type: ifcopenshell.entity_instance
    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :return: A tuple representing the XYZ centroid
    :rtype: npt.NDArray[np.float64]
    """
    centroid = get_bbox_centroid(geometry)
    if not element.ObjectPlacement or not element.ObjectPlacement.is_a("IfcLocalPlacement"):
        return np.array(centroid)
    mat = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
    return (mat @ np.array([*centroid, 1.0]))[0:3]


def get_shape_bbox_centroid(shape: ShapeType, geometry: ShapeType) -> npt.NDArray[np.float64]:
    """Calculates the shape's bounding box centroid

    The centroid is in global coordinates. Note that if you do not have the
    shape, you can use ``get_element_bbox_centroid``.

    :param shape: Shape output calculated by IfcOpenShell
    :type shape: shape
    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :return: A tuple representing the XYZ centroid
    :rtype: npt.NDArray[np.float64]
    """
    centroid = get_bbox_centroid(geometry)
    return (get_shape_matrix(shape) @ np.array([*centroid, 1.0]))[0:3]


def get_vertices(geometry: ShapeType) -> npt.NDArray[np.float64]:
    """Get all the vertices as a numpy array

    Vertices are in local coordinates.

    Results are a nested numpy array e.g. [[v1x, v1y, v1z], [v2x, v2y, v2z], ...]

    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :return: A numpy array listing all the vertices. Each vertex is a numpy array with XYZ coordinates.
    :rtype: np.array[np.array[float]]
    """
    return np.frombuffer(geometry.verts_buffer, "d").reshape(-1, 3)


def get_edges(geometry: ShapeType) -> npt.NDArray[np.int32]:
    """Get all the edges as a numpy array

    Results are a nested numpy array e.g. [[e1v1, e1v2], [e2v1, e2v2], ...]

    Note that although geometry always holds triangulated faces, edges will
    represent the original tessellation or BRep's faces, which may be quads or
    ngons.

    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :return: A numpy array listing all the edges. Each edge is a numpy array with two vertex indices.
    :rtype: np.array[np.array[int]]
    """
    return np.frombuffer(geometry.edges_buffer, dtype="i").reshape(-1, 2)


def get_faces(geometry: ShapeType) -> npt.NDArray[np.int32]:
    """Get all the faces as a numpy array

    Faces are always triangulated. If the shape is a BRep and you want to get
    the original untriangulated output, refer to ``get_edges``.

    Results are a nested numpy array e.g. [[f1v1, f1v2, f1v3], [f2v1, f2v2, f2v3], ...]

    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :return: A numpy array listing all the faces. Each face is a numpy array with three vertex indices.
    :rtype: np.array[np.array[int]]
    """
    return np.frombuffer(geometry.faces_buffer, dtype="i").reshape(-1, 3)


def get_representation_item_ids(geometry: ShapeType) -> npt.NDArray[np.int32]:
    """Get representation item ids for the geometry faces."""
    return np.frombuffer(geometry.item_ids_buffer, dtype="i")


def get_shape_vertices(shape: ShapeType, geometry: ShapeType) -> npt.NDArray[np.float64]:
    """Get the shape's vertices as a numpy array

    Vertices are in global coordinates. If you do not have the shape, you can
    use ``get_element_vertices``.

    Results are a nested numpy array e.g. [[v1x, v1y, v1z], [v2x, v2y, v2z], ...]

    :param shape: Shape output calculated by IfcOpenShell
    :type shape: shape
    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :return: A numpy array listing all the vertices. Each vertex is a numpy array with XYZ coordinates.
    :rtype: np.array[np.array[float]]
    """
    verts = get_vertices(geometry)
    mat = get_shape_matrix(shape)
    return np.delete((mat @ np.hstack((verts, np.ones((len(verts), 1)))).T).T, -1, axis=1)


def get_element_vertices(element: ifcopenshell.entity_instance, geometry: ShapeType) -> npt.NDArray[np.float64]:
    """Get the element's vertices as a numpy array

    Vertices are in global coordinates. Note that if you have the shape, it is
    more efficient to use ``get_shape_vertices``.

    Results are a nested numpy array e.g. [[v1x, v1y, v1z], [v2x, v2y, v2z], ...]

    :param element: The element occurrence
    :type: ifcopenshell.entity_instance
    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :return: A numpy array listing all the vertices. Each vertex is a numpy array with XYZ coordinates.
    :rtype: np.array[np.array[float]]
    """
    verts = get_vertices(geometry)
    if not element.ObjectPlacement or not element.ObjectPlacement.is_a("IfcLocalPlacement"):
        return verts
    mat = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
    return np.delete((mat @ np.hstack((verts, np.ones((len(verts), 1)))).T).T, -1, axis=1)


def get_bottom_elevation(geometry: ShapeType) -> float:
    """Gets the lowest local Z ordinate of the geometry

    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :return: The Z value
    :rtype: float
    """
    z_values = [geometry.verts[i + 2] for i in range(0, len(geometry.verts), 3)]
    return min(z_values)


def get_top_elevation(geometry: ShapeType) -> float:
    """Gets the highest local Z ordinate of the geometry

    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :return: The Z value
    :rtype: float
    """
    verts_flat = get_vertices(geometry).ravel()
    return np.max(verts_flat[2::3])


def get_shape_bottom_elevation(shape: ShapeType, geometry: ShapeType) -> float:
    """Gets the lowest global Z ordinate of the shape

    If you do not have the shape, you can use ``get_element_bottom_elevation``
    instead.

    :param shape: Shape output calculated by IfcOpenShell
    :type shape: shape
    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :return: The Z value
    :rtype: float
    """
    return min([v[2] for v in get_shape_vertices(shape, geometry)])


def get_shape_top_elevation(shape: ShapeType, geometry: ShapeType) -> float:
    """Gets the highest global Z ordinate of the shape

    If you do not have the shape, you can use ``get_element_top_elevation``
    instead.

    :param shape: Shape output calculated by IfcOpenShell
    :type shape: shape
    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :return: The Z value
    :rtype: float
    """
    return max([v[2] for v in get_shape_vertices(shape, geometry)])


def get_element_bottom_elevation(element: ifcopenshell.entity_instance, geometry: ShapeType) -> float:
    """Gets the lowest global Z ordinate of the element

    Note that if you have the shape, it is more efficient to use
    ``get_shape_bottom_elevation``.

    :param element: The element occurrence
    :type: ifcopenshell.entity_instance
    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :return: The Z value
    :rtype: float
    """
    return min([v[2] for v in get_element_vertices(element, geometry)])


def get_element_top_elevation(element: ifcopenshell.entity_instance, geometry: ShapeType) -> float:
    """Gets the highest global Z ordinate of the element

    Note that if you have the shape, it is more efficient to use
    ``get_shape_top_elevation``.

    :param element: The element occurrence
    :type: ifcopenshell.entity_instance
    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :return: The Z value
    :rtype: float
    """
    return max([v[2] for v in get_element_vertices(element, geometry)])


def get_bbox(vertices: Iterable[VECTOR_3D]) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    """Gets the bounding box of vertices

    :param vertices: An iterable of vertices
    :type: iterable
    :return: The bounding box value represented as a tuple of two numpy arrays.
        The first holds the bottom left corner and the second holds the top
        right.  E.g.  (np.array([minx, miny, minz]), np.array([maxx, maxy,
        maxz]))
    :rtype: tuple[np.array[float]]
    """
    x_values = [v[0] for v in vertices]
    y_values = [v[1] for v in vertices]
    z_values = [v[2] for v in vertices]
    minx = min(x_values)
    maxx = max(x_values)
    miny = min(y_values)
    maxy = max(y_values)
    minz = min(z_values)
    maxz = max(z_values)
    return (np.array([minx, miny, minz]), np.array([maxx, maxy, maxz]))


def get_area_vf(vertices: npt.NDArray[np.float64], faces: npt.NDArray[np.int32]) -> float:
    """Calculates the surface area given a list of vertices and triangulated faces

    :param vertices: A list of 3D vertices, such as returned from get_vertices.
    :type: np.array[iterable[float]]
    :param faces: A list of faces, such as returned from get_faces.
    :type: np.array[iterable[int]]
    :return: The surface area.
    :rtype: float
    """
    # Calculate the triangle normal vectors
    v1 = vertices[faces[:, 1]] - vertices[faces[:, 0]]
    v2 = vertices[faces[:, 2]] - vertices[faces[:, 0]]
    triangle_normals = np.cross(v1, v2)

    # Normalize the normal vectors to get their length (i.e., triangle area)
    triangle_areas = np.linalg.norm(triangle_normals, axis=1) / 2

    # Sum up the areas to get the total area of the mesh
    mesh_area = np.sum(triangle_areas)

    return mesh_area


def get_area(geometry: ShapeType) -> float:
    """Calculates the surface area of the geometry

    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :return: The surface area.
    :rtype: float
    """
    vertices = get_vertices(geometry)
    faces = get_faces(geometry)
    return get_area_vf(vertices, faces)


def get_side_area(
    geometry: ShapeType,
    axis: AXIS_LITERAL = "Y",
    direction: Optional[VECTOR_3D] = None,
) -> float:
    """Calculates the total surface area of surfaces that are visible from the specified axis

    This is typically useful for calculating elevational areas. For example,
    you might want to calculate the side area of a wall (i.e. only one side,
    not both).

    Surfaces do not need to be exactly perpendicular in the direction of the
    specified axis. A surface is counted so long as it is visible from that
    axis.

    Note that this calculates the actual area, not the projected 2D area. If
    you want the projected area, use ``get_footprint_area``.

    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :param axis: Either X, Y, or Z. Defaults to Y, which is used for standard
        walls.
    :type axis: str
    :return: The surface area.
    :rtype: float
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
    normal_tol = 0.01  # Close to perpendicular, but with a fuzz for numerical tolerance
    dot_products = np.dot(triangle_normals, direction)
    filtered_face_indices = np.where(dot_products > normal_tol)[0]
    filtered_faces = faces[filtered_face_indices]
    return get_area_vf(vertices, filtered_faces)


def get_max_side_area(geometry: ShapeType) -> float:
    """Returns the maximum X, Y, or Z side area

    See :func:`get_side_area` for how side area is calculated.

    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :return: The maximum surface area from either the X, Y, or Z axis.
    :rtype: float
    """
    return max(get_side_area(geometry, axis="X"), get_side_area(geometry, axis="Y"), get_side_area(geometry, axis="Z"))


def get_footprint_area(
    geometry: ShapeType,
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
    area. If you want the actual area, use ``get_side_area``.

    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :param axis: Either X, Y, or Z. Defaults to Z.
    :type axis: str,optional
    :param direction: An XYZ iterable (e.g. (0., 0., 1.)). If a direction
        vector is specified, this overrides the axis argument.
    :type axis: iterable[float],optional
    :return: The surface area.
    :rtype: float
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


def get_outer_surface_area(geometry: ShapeType) -> float:
    """Calculates the outer surface area (i.e. all sides except for top and bottom)

    This is typically useful for calculating painted areas of beams which
    exclude the end faces (at the minimum and maximum local Z).

    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :return: The surface area.
    :rtype: float
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


def get_footprint_perimeter(geometry: ShapeType) -> float:
    """Calculates the footprint perimeter of the geometry

    All faces with a negative Z normal are considered and the distance of all
    perimeter edges are totaled.

    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :return: The perimeter length
    :rtype: float
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

    return sum([np.linalg.norm(vertices[e[0]] - vertices[e[1]]) for e in (all_edges - shared_edges)])


def get_profiles(element: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    """Gets all 2D profiles used in the definition of a parametric shape

    Profiles may be retrieved either from material profile sets or from swept
    solid extrusions. This is useful for later doing 2D take-off from profiles.

    :param element: The element occurrence
    :type: ifcopenshell.entity_instance
    :return: A list of profiles
    :rtype: list[ifcopenshell.entity_instance]
    """
    material = ifcopenshell.util.element.get_material(element, should_skip_usage=True)
    if material and material.is_a("IfcMaterialProfileSet"):
        return [mp.Profile for mp in material.MaterialProfiles]
    return [e.SweptArea for e in get_extrusions(element)]


def get_extrusions(element: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
    """Gets all extruded area solids used to define an element's model body geometry

    :param element: The element occurrence
    :type: ifcopenshell.entity_instance
    :return: A list of extrusion representation items
    :rtype: list[ifcopenshell.entity_instance]
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


def get_total_edge_length(geometry: ShapeType) -> float:
    """Calculates the total length of edges in a given geometry.

    :param geometry: Geometry output calculated by IfcOpenShell
    :type geometry: geometry
    :return: The total length of all edges in the geometry.
    :rtype: float
    """
    vertices = get_vertices(geometry)
    vertices = vertices[get_edges(geometry)]
    return np.linalg.norm(vertices[:, 1] - vertices[:, 0], axis=1).sum()
