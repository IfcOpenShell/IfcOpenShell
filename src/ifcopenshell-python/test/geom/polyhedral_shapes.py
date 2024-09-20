import collections
import ifcopenshell
import ifcopenshell.geom

import pytest

from test.bootstrap import file


@pytest.mark.parametrize("file", ["geom/polygonal-face-tessellation.ifc"], indirect=True)
def test_polyhedral_setting(file):
    s = ifcopenshell.geom.settings()
    # default is triangle mesh
    assert s.get("triangulation-type") == ifcopenshell.ifcopenshell_wrapper.TRIANGLE_MESH
    s = ifcopenshell.geom.settings(TRIANGULATION_TYPE=ifcopenshell.ifcopenshell_wrapper.POLYHEDRON_WITHOUT_HOLES)
    obj = ifcopenshell.geom.create_shape(s, file[30])
    # outer:
    #   - top
    #   - left
    #   - bottom
    #   - right
    #   - back;
    # inner:
    #   - top
    #   - left
    #   - bottom
    #   - right
    #   - back;
    # front:
    #   - 8 triangles
    # --------------------- +
    #     18 facets
    assert len(obj.geometry.faces) == 18
    s = ifcopenshell.geom.settings(TRIANGULATION_TYPE=ifcopenshell.ifcopenshell_wrapper.POLYHEDRON_WITH_HOLES)
    obj = ifcopenshell.geom.create_shape(s, file[30])
    # outer:
    #   - top
    #   - left
    #   - bottom
    #   - right
    #   - back;
    # inner:
    #   - top
    #   - left
    #   - bottom
    #   - right
    #   - back;
    # front:
    #   - single facet with 2 bounds
    # --------------------- +
    #     11 facets
    assert len(obj.geometry.faces) == 11
    # 10 facets with 1 bound, 1 facet with 2 bounds
    assert sorted(collections.Counter(map(len, obj.geometry.faces)).items()) == [(1, 10), (2, 1)]
