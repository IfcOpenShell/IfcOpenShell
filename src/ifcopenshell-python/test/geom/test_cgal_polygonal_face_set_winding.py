"""Regression cases for https://github.com/IfcOpenShell/IfcOpenShell/issues/10296.

Check orientation using geometric edges as well as mesh indices: cutting a seam
by duplicating its vertices must not hide incompatible face winding.
"""

from collections import Counter

import numpy as np
import pytest

import ifcopenshell
import ifcopenshell.geom

CUBE_POINTS = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0), (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]
CUBE_FACES = [
    (0, 2, 1),
    (0, 3, 2),
    (4, 5, 6),
    (4, 6, 7),
    (0, 1, 5),
    (0, 5, 4),
    (1, 2, 6),
    (1, 6, 5),
    (2, 3, 7),
    (2, 7, 6),
    (3, 0, 4),
    (3, 4, 7),
]
STRIP_POINTS = [
    (0, 4.6, 4),
    (6.9, 4.6, 4),
    (6.9, 3.9, 4),
    (6.9, 0.4, 4),
    (6.9, 0, 0),
    (6.9, 0.4, 0),
    (6.9, 3.9, 0),
    (6.9, 4.6, 0),
    (0, 4.6, 0),
    (5.8, 3.8, 0),
]
# Only the floor triangle (first) disagrees with its neighbour.
STRIP_FACES = [(9, 4, 5), (3, 4, 5), (2, 3, 5), (2, 5, 6), (1, 2, 6), (1, 6, 7), (7, 0, 1), (7, 8, 0)]

KERNEL_SETTINGS = [
    pytest.param(
        kernel,
        reorient_shells,
        marks=pytest.mark.skipif(
            not ifcopenshell.geom.has_geometry_library(kernel),
            reason=f"{kernel} geometry kernel is unavailable",
        ),
    )
    for kernel in ("cgal-simple", "cgal", "opencascade")
    for reorient_shells in (False, True)
    # OpenCASCADE only promises to repair winding when explicitly requested.
    if kernel != "opencascade" or reorient_shells
]


def polygonal_face_set_geometry(points, faces, kernel, reorient_shells):
    model = ifcopenshell.file(schema="IFC4")
    face_set = model.createIfcPolygonalFaceSet(
        model.createIfcCartesianPointList3D([tuple(float(c) for c in p) for p in points]),
        None,
        [model.createIfcIndexedPolygonalFace([v + 1 for v in face]) for face in faces],
        None,
    )
    settings = ifcopenshell.geom.settings()
    settings.set("weld-vertices", True)
    settings.set("reorient-shells", reorient_shells)
    geometry = ifcopenshell.geom.create_shape(settings, face_set, geometry_library=kernel)
    return np.array(geometry.verts).reshape(-1, 3), np.array(geometry.faces).reshape(-1, 3)


def assert_consistent_mesh(vertices, triangles, points, face_count, boundary_edge_count):
    assert len(triangles) == face_count
    positions = [tuple(float(c) for c in p) for p in np.round(vertices, 6)]
    assert set(positions) == {tuple(p) for p in points}
    directed = Counter()
    undirected = Counter()
    for triangle in triangles:
        corners = [positions[v] for v in triangle]
        assert len(set(corners)) == 3
        for a, b in zip(corners, corners[1:] + corners[:1]):
            directed[a, b] += 1
            undirected[tuple(sorted((a, b)))] += 1
    clashes = {edge: uses for edge, uses in directed.items() if uses > 1}
    assert not clashes, f"Geometric edges traversed twice in the same direction: {clashes}"
    assert all(uses <= 2 for uses in undirected.values())
    assert sum(uses == 1 for uses in undirected.values()) == boundary_edge_count
    assert len(vertices) == len(points), "Unexpected duplicated seam vertices"


def signed_volume(vertices, triangles):
    # Keep the sign: util.shape.get_volume() takes the absolute value.
    a, b, c = vertices[triangles].transpose(1, 0, 2)
    return np.einsum("ij,ij->i", a, np.cross(b, c)).sum() / 6


@pytest.mark.parametrize("kernel,reorient_shells", KERNEL_SETTINGS)
@pytest.mark.parametrize("winding", ["outward", "first-reversed", "last-reversed", "inward"])
def test_cube_winding(kernel, reorient_shells, winding):
    faces = list(CUBE_FACES)
    if winding == "inward":
        faces = [face[::-1] for face in faces]
    elif winding == "first-reversed":
        faces[0] = faces[0][::-1]
    elif winding == "last-reversed":
        faces[-1] = faces[-1][::-1]
    vertices, triangles = polygonal_face_set_geometry(CUBE_POINTS, faces, kernel, reorient_shells)
    assert_consistent_mesh(vertices, triangles, CUBE_POINTS, 12, 0)
    if reorient_shells:
        assert signed_volume(vertices, triangles) == pytest.approx(1.0)


@pytest.mark.parametrize("kernel,reorient_shells", KERNEL_SETTINGS)
@pytest.mark.parametrize("voids_inwards", [False, True], ids=["voids-outwards", "voids-inwards"])
def test_hollow_cube_winding(kernel, reorient_shells, voids_inwards):
    model = ifcopenshell.file(schema="IFC4")
    outer_points = np.array(CUBE_POINTS, dtype=float)
    outer_faces = np.array(CUBE_FACES, dtype=int)
    points = np.concatenate((outer_points, outer_points * 0.5 + 0.25))
    void_faces = outer_faces + len(outer_points)
    if voids_inwards:
        void_faces = void_faces[:, ::-1]
    ifc_points = [model.createIfcCartesianPoint(p.tolist()) for p in points]

    def shell(faces):
        return model.createIfcClosedShell(
            [
                model.createIfcFace(
                    [model.createIfcFaceOuterBound(model.createIfcPolyLoop([ifc_points[v] for v in face]), True)]
                )
                for face in faces
            ]
        )

    # Concrete subtype of IfcManifoldSolidBrep carrying the Voids attribute.
    brep = model.createIfcFacetedBrepWithVoids(shell(outer_faces), [shell(void_faces)])
    settings = ifcopenshell.geom.settings()
    settings.set("weld-vertices", True)
    settings.set("reorient-shells", reorient_shells)
    geometry = ifcopenshell.geom.create_shape(settings, brep, geometry_library=kernel)
    vertices = np.array(geometry.verts).reshape(-1, 3)
    triangles = np.array(geometry.faces).reshape(-1, 3)
    assert_consistent_mesh(vertices, triangles, points, 24, 0)
    inner = np.all((vertices[triangles] >= 0.25) & (vertices[triangles] <= 0.75), axis=(1, 2))
    assert np.count_nonzero(inner) == 12
    assert signed_volume(vertices, triangles[~inner]) == pytest.approx(1.0)
    assert signed_volume(vertices, triangles[inner]) == pytest.approx(-0.125)
    assert signed_volume(vertices, triangles) == pytest.approx(0.875)


@pytest.mark.parametrize("kernel,reorient_shells", KERNEL_SETTINGS)
@pytest.mark.parametrize("coordinates", ["decimal", "binary-exact"])
@pytest.mark.parametrize("order", ["original", "rotated", "reversed", "consistent"])
def test_open_strip_winding(kernel, reorient_shells, coordinates, order):
    faces = list(STRIP_FACES)
    if order == "rotated":
        faces = faces[1:] + faces[:1]
    elif order == "reversed":
        faces.reverse()
    elif order == "consistent":
        faces[0] = faces[0][::-1]
    points = STRIP_POINTS
    if coordinates == "binary-exact":
        # Same topology with exactly representable coordinates. Interpolating
        # decimal edge endpoints can produce 0.3999999999999999 versus 0.4,
        # which the CGAL builder's exact point map treats as different vertices.
        points = [tuple(round(c * 4) / 4 for c in point) for point in points]
    vertices, triangles = polygonal_face_set_geometry(points, faces, kernel, reorient_shells)
    # Open surfaces have no preferred outward direction or meaningful volume.
    assert_consistent_mesh(vertices, triangles, points, 8, 10)
