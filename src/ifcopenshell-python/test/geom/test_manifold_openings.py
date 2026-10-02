# This file was generated with the assistance of an AI coding tool.

from pathlib import Path

import pytest

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell.util.shape

pytestmark = pytest.mark.skipif(
    not ifcopenshell.geom.has_geometry_library("manifold"), reason="manifold geometry kernel is unavailable"
)

FIXTURE = Path(__file__).parent.parent / "fixtures" / "geom" / "wall_two_openings_manifold_9762.ifc"


def test_wall_with_two_openings_converts_with_manifold_9762():
    model = ifcopenshell.open(str(FIXTURE))
    wall = model.by_type("IfcWall")[0]
    body = next(r for r in wall.Representation.Representations if r.RepresentationIdentifier == "Body")
    settings = ifcopenshell.geom.settings()
    for _ in range(20):
        shape = ifcopenshell.geom.create_shape(settings, wall, body, geometry_library="manifold")
        assert len(shape.geometry.verts) > 0
        assert len(shape.geometry.faces) > 0
        assert ifcopenshell.util.shape.get_volume(shape.geometry) == pytest.approx(0.2557, rel=1e-3)
