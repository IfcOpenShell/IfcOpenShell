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

import numpy as np
import ifcopenshell.util.element
import ifcopenshell.util.placement
import ifcopenshell.util.representation

tol = 1e-6


def is_x(value, x, tolerance=None):
    if tolerance is None:
        tolerance = tol
    return abs(x - value) < tolerance


def get_volume(geometry):
    # https://stackoverflow.com/questions/1406029/how-to-calculate-the-volume-of-a-3d-mesh-object-the-surface-of-which-is-made-up
    def signed_triangle_volume(p1, p2, p3):
        v321 = p3[0] * p2[1] * p1[2]
        v231 = p2[0] * p3[1] * p1[2]
        v312 = p3[0] * p1[1] * p2[2]
        v132 = p1[0] * p3[1] * p2[2]
        v213 = p2[0] * p1[1] * p3[2]
        v123 = p1[0] * p2[1] * p3[2]
        return (1.0 / 6.0) * (-v321 + v231 + v312 - v132 - v213 + v123)

    verts = geometry.verts
    faces = geometry.faces
    grouped_verts = [[verts[i], verts[i + 1], verts[i + 2]] for i in range(0, len(verts), 3)]
    volumes = [
        signed_triangle_volume(grouped_verts[faces[i]], grouped_verts[faces[i + 1]], grouped_verts[faces[i + 2]])
        for i in range(0, len(faces), 3)
    ]
    return abs(sum(volumes))


def get_x(geometry):
    x_values = [geometry.verts[i] for i in range(0, len(geometry.verts), 3)]
    return max(x_values) - min(x_values)


def get_y(geometry):
    y_values = [geometry.verts[i + 1] for i in range(0, len(geometry.verts), 3)]
    return max(y_values) - min(y_values)


def get_z(geometry):
    z_values = [geometry.verts[i + 2] for i in range(0, len(geometry.verts), 3)]
    return max(z_values) - min(z_values)


def get_shape_matrix(shape):
    m = shape.transformation.matrix.data
    return np.array(([m[0], m[3], m[6], m[9]], [m[1], m[4], m[7], m[10]], [m[2], m[5], m[8], m[11]], [0, 0, 0, 1]))


def get_bbox_centroid(geometry):
    x_values = [geometry.verts[i] for i in range(0, len(geometry.verts), 3)]
    y_values = [geometry.verts[i + 1] for i in range(0, len(geometry.verts), 3)]
    z_values = [geometry.verts[i + 2] for i in range(0, len(geometry.verts), 3)]
    minx = min(x_values)
    maxx = max(x_values)
    miny = min(y_values)
    maxy = max(y_values)
    minz = min(z_values)
    maxz = max(z_values)
    return (minx + ((maxx - minx) / 2), miny + ((maxy - miny) / 2), minz + ((maxz - minz) / 2))


def get_element_bbox_centroid(element, geometry):
    centroid = get_bbox_centroid(geometry)
    if not element.ObjectPlacement or not element.ObjectPlacement.is_a("IfcLocalPlacement"):
        return centroid
    mat = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
    return (mat @ np.array([*centroid, 1.0]))[0:3]


def get_shape_bbox_centroid(shape, geometry):
    centroid = get_bbox_centroid(geometry)
    return (get_shape_matrix(shape) @ np.array([*centroid, 1.0]))[0:3]


def get_vertices(geometry):
    verts = geometry.verts
    return np.array([np.array([verts[i], verts[i + 1], verts[i + 2]]) for i in range(0, len(verts), 3)])


def get_edges(geometry):
    edges = geometry.edges
    return [[edges[i], edges[i + 1]] for i in range(0, len(edges), 2)]


def get_faces(geometry):
    faces = geometry.faces
    return [[faces[i], faces[i + 1], faces[i + 2]] for i in range(0, len(faces), 3)]


def get_shape_vertices(shape, geometry):
    verts = get_vertices(geometry)
    mat = get_shape_matrix(shape)
    return np.array([mat @ np.array([verts[i], verts[i + 1], verts[i + 2]]) for i in range(0, len(verts), 3)])


def get_element_vertices(element, geometry):
    verts = get_vertices(geometry)
    if not element.ObjectPlacement or not element.ObjectPlacement.is_a("IfcLocalPlacement"):
        return verts
    mat = ifcopenshell.util.placement.get_local_placement(element.ObjectPlacement)
    return np.array([mat @ np.array([verts[i], verts[i + 1], verts[i + 2]]) for i in range(0, len(verts), 3)])


def get_bottom_elevation(geometry):
    z_values = [geometry.verts[i + 2] for i in range(0, len(geometry.verts), 3)]
    return min(z_values)


def get_top_elevation(geometry):
    z_values = [geometry.verts[i + 2] for i in range(0, len(geometry.verts), 3)]
    return max(z_values)


def get_shape_bottom_elevation(shape, geometry):
    return min([v[2] for v in get_shape_vertices(shape, geometry)])


def get_shape_top_elevation(shape, geometry):
    return max([v[2] for v in get_shape_vertices(shape, geometry)])


def get_element_bottom_elevation(element, geometry):
    return min([v[2] for v in get_element_vertices(element, geometry)])


def get_element_top_elevation(element, geometry):
    return max([v[2] for v in get_element_vertices(element, geometry)])


def get_bbox(vertices):
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


def get_area_vf(vertices, faces):
    # Calculate the triangle normal vectors
    v1 = vertices[faces[:, 1]] - vertices[faces[:, 0]]
    v2 = vertices[faces[:, 2]] - vertices[faces[:, 0]]
    triangle_normals = np.cross(v1, v2)

    # Normalize the normal vectors to get their length (i.e., triangle area)
    triangle_areas = np.linalg.norm(triangle_normals, axis=1) / 2

    # Sum up the areas to get the total area of the mesh
    mesh_area = np.sum(triangle_areas)

    return mesh_area


def get_area(geometry):
    verts = geometry.verts
    faces = geometry.faces
    vertices = np.array([[verts[i], verts[i + 1], verts[i + 2]] for i in range(0, len(verts), 3)])
    faces = np.array([[faces[i], faces[i + 1], faces[i + 2]] for i in range(0, len(faces), 3)])
    return get_area_vf(vertices, faces)


def get_side_area(geometry, axis="Y"):
    verts = geometry.verts
    faces = geometry.faces
    vertices = np.array([[verts[i], verts[i + 1], verts[i + 2]] for i in range(0, len(verts), 3)])
    faces = np.array([[faces[i], faces[i + 1], faces[i + 2]] for i in range(0, len(faces), 3)])

    # Calculate the triangle normal vectors
    v1 = vertices[faces[:, 1]] - vertices[faces[:, 0]]
    v2 = vertices[faces[:, 2]] - vertices[faces[:, 0]]
    triangle_normals = np.cross(v1, v2)

    # Normalize the normal vectors
    triangle_normals = triangle_normals / np.linalg.norm(triangle_normals, axis=1)[:, np.newaxis]

    # Find the faces with a normal vector pointing in the desired +Y normal direction
    axis = {"X": 0, "Y": 1, "Z": 2}[axis]
    filtered_face_indices = np.where(triangle_normals[:, axis] > tol)[0]
    filtered_faces = faces[filtered_face_indices]
    return get_area_vf(vertices, filtered_faces)


def get_footprint_area(geometry):
    verts = geometry.verts
    faces = geometry.faces
    vertices = np.array([[verts[i], verts[i + 1], verts[i + 2]] for i in range(0, len(verts), 3)])
    faces = np.array([[faces[i], faces[i + 1], faces[i + 2]] for i in range(0, len(faces), 3)])

    # Calculate the triangle normal vectors
    v1 = vertices[faces[:, 1]] - vertices[faces[:, 0]]
    v2 = vertices[faces[:, 2]] - vertices[faces[:, 0]]
    triangle_normals = np.cross(v1, v2)

    # Normalize the normal vectors
    triangle_normals = triangle_normals / np.linalg.norm(triangle_normals, axis=1)[:, np.newaxis]

    # Find the faces with a normal vector pointing in the desired +Z normal direction
    filtered_face_indices = np.where(triangle_normals[:, 2] > tol)[0]
    filtered_faces = faces[filtered_face_indices]
    return get_area_vf(vertices, filtered_faces)


def get_outer_surface_area(geometry):
    verts = geometry.verts
    faces = geometry.faces
    vertices = np.array([[verts[i], verts[i + 1], verts[i + 2]] for i in range(0, len(verts), 3)])
    faces = np.array([[faces[i], faces[i + 1], faces[i + 2]] for i in range(0, len(faces), 3)])

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


def get_footprint_perimeter(geometry):
    verts = geometry.verts
    faces = geometry.faces
    vertices = np.array([[verts[i], verts[i + 1], verts[i + 2]] for i in range(0, len(verts), 3)])
    faces = np.array([[faces[i], faces[i + 1], faces[i + 2]] for i in range(0, len(faces), 3)])

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


def get_profiles(element):
    material = ifcopenshell.util.element.get_material(element, should_skip_usage=True)
    if material and material.is_a("IfcMaterialProfileSet"):
        return [mp.Profile for mp in material.MaterialProfiles]
    return [e.SweptArea for e in get_extrusions(element)]


def get_extrusions(element):
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
