from pathlib import Path

import numpy as np
import pytest

import ifcopenshell
import ifcopenshell.geom


@pytest.mark.parametrize("geometry_library", ["opencascade", "hybrid-cgal-simple-opencascade", "manifold"])
def test_bug_9748(geometry_library):
    # https://github.com/IfcOpenShell/IfcOpenShell/issues/9748
    path = Path(__file__).parent.parent / "fixtures/geom/manifold_vert_attr_count_bug_9748.ifc"
    model = ifcopenshell.open(path)
    _ = [
        *ifcopenshell.geom.consume_iterator(
            ifcopenshell.geom.iterator(ifcopenshell.geom.settings(), model, geometry_library=geometry_library)
        )
    ]
    assert True  # No crash


def test_manifold_emits_normals():
    path = Path(__file__).parent.parent / "fixtures/geom/manifold_vert_attr_count_bug_9748.ifc"
    model = ifcopenshell.open(path)
    settings = ifcopenshell.geom.settings()
    settings.set("weld-vertices", False)
    shapes = [
        *ifcopenshell.geom.consume_iterator(ifcopenshell.geom.iterator(settings, model, geometry_library="manifold"))
    ]

    assert shapes
    for shape in shapes:
        assert len(shape.geometry.normals) == len(shape.geometry.verts)
        assert any(component != 0.0 for component in shape.geometry.normals)


def test_manifold_mesh_fallback_emits_normals():
    path = Path(__file__).parent.parent / "fixtures/rules/pass-shaperep-surfacemodel-surface-model-ifc2x3.ifc"
    model = ifcopenshell.open(path)
    model.by_type("IfcFaceOuterBound")[0].Orientation = True
    settings = ifcopenshell.geom.settings()
    settings.set("weld-vertices", False)

    geometry = ifcopenshell.geom.create_shape(
        settings,
        model.by_type("IfcShapeRepresentation")[0],
        geometry_library="manifold",
    )

    assert geometry.verts
    assert len(geometry.normals) == len(geometry.verts)
    assert all(component == pytest.approx(expected) for component, expected in zip(geometry.normals, (0, 0, 1) * 4))


def mesh_fallback_geometry(points, triangles, *, weld=False, omit_normals=False):
    model = ifcopenshell.file(schema="IFC4")
    surface = model.create_entity(
        "IfcTriangulatedFaceSet",
        Coordinates=model.create_entity("IfcCartesianPointList3D", CoordList=points),
        Closed=False,
        CoordIndex=triangles,
    )
    settings = ifcopenshell.geom.settings()
    settings.set("weld-vertices", weld)
    settings.set("no-normals", omit_normals)
    return ifcopenshell.geom.create_shape(settings, surface, geometry_library="manifold")


@pytest.mark.parametrize("angle", [0.0, 5.0, 9.9, 10.1, 90.0])
@pytest.mark.parametrize("weld,omit_normals", [(False, False), (False, True), (True, False)])
def test_manifold_mesh_fallback_smoothing_angle(angle, weld, omit_normals):
    radians = np.radians(angle)
    # Unequal triangle areas verify that unit face normals are averaged equally.
    points = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, -2.0 * np.cos(radians), 2.0 * np.sin(radians))]
    geometry = mesh_fallback_geometry(points, [(1, 2, 3), (2, 1, 4)], weld=weld, omit_normals=omit_normals)
    vertices = np.array(geometry.verts).reshape(-1, 3)
    faces = np.array(geometry.faces).reshape(-1, 3)
    edges = np.array(geometry.edges).reshape(-1, 2)
    smooth = angle < 10.0
    assert len(vertices) == (4 if smooth or weld else 6)
    # The shared edge is a border only when the faces belong to different components.
    shared_borders = sum(np.allclose(vertices[edge].mean(axis=0), (0.5, 0.0, 0.0)) for edge in edges)
    assert bool(shared_borders) == (not smooth)
    if weld or omit_normals:
        assert not geometry.normals
        return
    normals = np.array(geometry.normals).reshape(-1, 3)
    expected = np.array([(0.0, 0.0, 1.0), (0.0, np.sin(radians), np.cos(radians))])
    for face, normal in zip(faces, expected):
        for index in face:
            if smooth and np.allclose(vertices[index][1:], (0.0, 0.0)):
                average = expected.sum(axis=0)
                assert normals[index] == pytest.approx(average / np.linalg.norm(average))
            else:
                assert normals[index] == pytest.approx(normal)


@pytest.mark.parametrize("triangles", [[(1, 2, 3), (1, 4, 5)], [(1, 2, 3), (2, 1, 4), (1, 2, 5)]])
def test_manifold_mesh_fallback_separates_nonmanifold_connections(triangles):
    points = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, -1.0, 0.0), (1.0, 2.0, 0.0)]
    geometry = mesh_fallback_geometry(points, triangles)
    assert len(geometry.verts) == len(triangles) * 9
    faces = np.array(geometry.faces).reshape(-1, 3)
    assert len(set(faces.flat)) == len(triangles) * 3
    assert len(geometry.edges) == len(triangles) * 6


def test_manifold_mesh_fallback_flood_fill_is_transitive():
    points = [(0.0, 0.0, 0.0), (0.0, 1.0, 0.0)]
    triangles = []
    x = z = 0.0
    for i, angle in enumerate([0.0, 7.0, 14.0]):
        x += np.cos(np.radians(angle))
        z += np.sin(np.radians(angle))
        points.extend([(x, 0.0, z), (x, 1.0, z)])
        a = 2 * i + 1
        triangles.extend([(a, a + 2, a + 1), (a + 1, a + 2, a + 3)])
    geometry = mesh_fallback_geometry(points, triangles)
    # Every adjacent pair is within 10 degrees, although the end faces are not.
    assert len(geometry.verts) == 8 * 3
    assert len(geometry.edges) == 8 * 2
    normals = np.array(geometry.normals).reshape(-1, 3)
    assert np.linalg.norm(normals, axis=1) == pytest.approx(np.ones(8))
