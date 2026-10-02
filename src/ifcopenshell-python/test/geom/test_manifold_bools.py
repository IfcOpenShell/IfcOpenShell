from pathlib import Path

import ifcopenshell
import ifcopenshell.geom


def test_bug_9748():
    # https://github.com/IfcOpenShell/IfcOpenShell/issues/9748
    path = Path(__file__).parent.parent / "fixtures/geom/manifold_vert_attr_count_bug_9748.ifc"
    model = ifcopenshell.open(path)
    ifcopenshell.geom.consume_iterator(
        ifcopenshell.geom.iterator(ifcopenshell.geom.settings(), model, geometry_library="manifold")
    )
    assert True  # No crash
