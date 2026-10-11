from pathlib import Path

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
