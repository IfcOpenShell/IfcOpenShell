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
